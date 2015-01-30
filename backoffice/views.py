# -*- coding: utf-8 -*-

import logging
import os
import json
import random

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _


from capa.xqueue_interface import make_hashkey
from courseware.courses import course_image_url, get_course_about_section, get_courses, get_cms_course_link
from instructor_task.api_helper import AlreadyRunningError
from instructor_task.api import get_instructor_task_history
from instructor.views.legacy import get_background_task_table
from util.json_request import JsonResponse
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole
from xmodule.modulestore.django import modulestore

from backoffice.forms import StudentCertificateForm, FirstRequiredFormSet
from fun_certificates.generator import CertificateInfo
from fun_instructor.api import submit_generate_certificate, get_running_instructor_tasks
from universities.models import University

from .models import Course, Teacher

ABOUT_SECTION_FIELDS = ['title', 'university']


log = logging.getLogger(__name__)


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)


def course_infos(course):
    for section in ABOUT_SECTION_FIELDS:
        setattr(course, section, get_course_about_section(course, section))
    setattr(course, 'course_image_url', course_image_url(course))
    setattr(course, 'students_count', CourseEnrollment.objects.filter(course_id=course.id).count())
    return course


def get_course(course_key_string):
    """
    Return the edX course object  for a given course_key.
    """
    ck = CourseKey.from_string(course_key_string)
    course = modulestore().get_course(ck, depth=0)
    return course


@group_required('fun_backoffice')
def courses_list(request):
    courses = get_courses(request.user)

    courses = [course_infos(course) for course in courses]
    pattern = request.GET.get('search')

    if pattern:
        courses = [course for course in courses
                if pattern in course.title
                or pattern in course.id.to_deprecated_string()]

    return render(request, 'backoffice/courses.html', {
        'courses': courses,
        'pattern': pattern,
    })


@group_required('fun_backoffice')
def course_detail(request, course_key_string):
    """Course is deleted from Mongo and staff and students enrollments from mySQL.
    States and responses from students are not yet deleted from mySQL
    (StudentModule, StudentModuleHistory are very big tables)."""
    course = course_infos(get_course(course_key_string))
    ck = CourseKey.from_string(course_key_string)
    funcourse, created = Course.objects.get_or_create(key=ck)
    if created:
        funcourse.university = University.objects.get(slug=ck.org)
        funcourse.save()


    TeacherFormSet = inlineformset_factory(Course, Teacher, formset=FirstRequiredFormSet, can_delete=True)
    teacher_formset = TeacherFormSet(instance=funcourse, data=request.POST or None)

    if request.method == 'POST':
        if request.POST['action'] == 'delete-course':
            # from xmodule.contentstore.utils.delete_course_and_groups function
            module_store = modulestore()
            with module_store.bulk_operations(ck):
                module_store.delete_course(ck, request.user.id)

            CourseAccessRole.objects.filter(course_id=ck).delete()  # shall we also delete student's enrollments ?
            funcourse.delete()
            messages.warning(request, _(u"Course <strong>%s</strong> has been deleted.") % course.id)
            log.warning('Course %s deleted by user %s' % (course.id, request.user.username))
            return redirect(courses_list)

        elif request.POST['action'] == 'update-teachers' and teacher_formset.is_valid():
            teacher_formset.save()

            messages.success(request, _(u"Teachers have been updated"))
            return redirect(courses_list)

    try:
        university = University.objects.get(code=course.org)
    except University.DoesNotExist:
        university = None

    studio_url = get_cms_course_link(course)
    roles = CourseAccessRole.objects.filter(course_id=ck)

    return render(request, 'backoffice/course.html', {
            'course': course,
            'studio_url': studio_url,
            'teacher_formset': teacher_formset,
            'university': university,
            'roles': roles,
        })



@group_required('fun_backoffice')
def course_certificate(request, course_key_string):
    course = get_course(course_key_string)
    ck = CourseKey.from_string(course_key_string)

    # generate list of pending background tasks
    instructor_tasks = get_running_instructor_tasks(ck, task_type='certificate-generation')

    for instructor_task in instructor_tasks:
            if instructor_task.task_output:
                instructor_task.task_output = json.loads(instructor_task.task_output)
            else:
                instructor_task.task_output = {'total' : 0,
                                               'downloadable' : 0,
                                               'notpassing': 0 }
    # generate list of previous background tasks

    instructor_tasks_history = get_instructor_task_history(ck, usage_key=None, student=None, )

    for instructor_task in instructor_tasks_history:
            if instructor_task.task_output:
                instructor_task.task_output = json.loads(instructor_task.task_output)
            else:
                instructor_task.task_output = {'total' : 0,
                                               'downloadable' : 0,
                                               'notpassing': 0 }
    # if instructor_tasks:
    #     import ipdb; ipdb.set_trace()
    teachers_form_set_factory = formset_factory(
        TeachersCertificateForm,
        extra=TeachersCertificateForm.MAX_TEACHERS,
        formset=RequiredFormSet
    )

    if request.method == 'POST':
        student_form = StudentCertificateForm(request.POST)
        if student_form.is_valid() and teachers_form_set.is_valid():
            try:
                university = University.objects.get(code=course.org)
            except University.DoesNotExist:
                messages.warning(request, _("University doesn't exist"))
                university = None
            if university is not None:
                certificate = generate_test_certificate(course, university, student_form, teachers_form_set)
                return certificate_file_response(certificate)
    else:
        student_form = StudentCertificateForm()

    return render(request, 'backoffice/certificate.html', {
            'course': course,
            'student_form_certificate' : student_form,
            'instructor_tasks' : instructor_tasks,
            'instructor_tasks_history' : instructor_tasks_history,
        })


def certificate_file_response(certificate):
    """
    Return the HttpResponse for downloading the certificate pdf file.
    """
    response = HttpResponse("", content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(certificate.filename)
    with open(certificate.pdf_file_name, 'r') as gradefile:
        response.write(gradefile.read())
    return response


def generate_test_certificate(course, university, student_form, teachers_form_set):
    """Generate the pdf certicate, save it on disk"""

    if university.certificate_logo:
        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
    else:
        logo_path = None

    # make a teachers/title list from the teachers_form_set
    teachers = [u"{}/{}".format(
        teacher.cleaned_data['full_name'],
        teacher.cleaned_data['title']
    )  for teacher in teachers_form_set if 'full_name' in teacher.cleaned_data and 'title' in teacher.cleaned_data]

    key = make_hashkey(random.random())
    filename = "TEST_attestation_suivi_%s_%s.pdf" % (
        course.id.to_deprecated_string().replace('/', '_'), key
    )

    certificate = CertificateInfo(
        student_form.cleaned_data['full_name'],
        course.display_name, university.name, logo_path,
        filename, teachers
    )
    certificate.generate()

    return certificate

@group_required('fun_backoffice')
def generate_certificate(request, course_key_string):
    """  """

    course_key = CourseKey.from_string(course_key_string)
    query_features = {'student' : '',
                      'problem_url' : '',
                      'email_id' : '',
                      'teachers' : 'jean/profs'}
    try:
        submit_generate_certificate(request, course_key, query_features)
        success_status = "OK"
        return JsonResponse({"status": success_status})
    except AlreadyRunningError:
        already_running_status = "attention"
        return JsonResponse({"status": already_running_status})

