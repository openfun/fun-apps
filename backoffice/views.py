# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
import datetime
import logging
import re
import tempfile

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext, ugettext_lazy as _

from courseware.courses import course_image_url, get_course_about_section, get_courses, get_cms_course_link
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole
from xmodule.modulestore.django import modulestore

from fun.management.commands.generate_oa_data import Command as OaCommand
from backoffice.forms import FirstRequiredFormSet
from backoffice.utils import get_course

from universities.models import University
from .models import Course, Teacher

ABOUT_SECTION_FIELDS = ['title', 'university', 'effort', 'video']

log = logging.getLogger(__name__)

FunCourse = namedtuple('FunCourse',
        'course, course_image_url, students_count, ' + ', '.join(ABOUT_SECTION_FIELDS))


def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)


def course_infos(course):
    """Annotate course object with complementary informations."""
    about_section = {}
    for section in ABOUT_SECTION_FIELDS:
        about_section[section] = get_course_about_section(course, section)
    about_section['effort'] = about_section['effort'].replace('\n', '')  # clean the CRs
    if about_section['video']:
        try:  # well, edx store the Youtube iframe html code, we extract it...
            about_section['video'] = re.findall('www.youtube.com/embed/(?P<hash>[\w]+)\?', about_section['video'])[0]
        except IndexError:
            pass
    course = FunCourse(course=course,
            course_image_url=course_image_url(course),
            students_count=CourseEnrollment.objects.filter(course_id=course.id).count(),
            **about_section
            )
    return course


@group_required('fun_backoffice')
def courses_list(request):
    courses = get_courses(request.user)

    courses = [course_infos(course) for course in courses]
    pattern = request.GET.get('search')

    if pattern:
        courses = [course for course in courses
                if pattern in course.title
                or pattern in course.course.id.to_deprecated_string()]

    if request.method == 'POST':
        # export as CSV
        filename = 'export-cours-%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        writer = csv.writer(response)
        csv_header = [ugettext(u"Title"), ugettext(u"University"), ugettext(u"Organisation code"),
                ugettext(u"Course"), ugettext(u"Run"), ugettext(u"Start date"), ugettext(u"End date"),
                ugettext(u"Enrollment start"), ugettext(u"Enrollment end"), ugettext(u"Students count"),
                ugettext(u"Effort"), ugettext(u"Image"), ugettext(u"Video"), ugettext(u"Url")]
        writer.writerow([field.encode('utf-8') for field in csv_header])

        for course in courses:
            raw = []
            raw.append(course.title.encode('utf-8'))
            raw.append(course.university.encode('utf-8'))
            raw.append(course.course.id.org)
            raw.append(course.course.id.course)
            raw.append(course.course.id.run)
            raw.append(course.course.start.strftime('%Y-%m-%d %H:%M')
                    if course.course.start else '')
            raw.append(course.course.end.strftime('%Y-%m-%d %H:%M')
                    if course.course.end else '')
            raw.append(course.course.enrollment_start.strftime('%Y-%m-%d %H:%M')
                    if course.course.enrollment_start else '')
            raw.append(course.course.enrollment_end.strftime('%Y-%m-%d %H:%M')
                    if course.course.enrollment_end else '')
            raw.append(course.students_count)
            raw.append(course.effort)
            raw.append('https://%s%s' % (settings.LMS_BASE, course.course_image_url))
            raw.append(course.video)
            raw.append('https://%s%s' % (settings.LMS_BASE,
                    reverse('about_course', args=[course.course.id.to_deprecated_string()])))
            writer.writerow(raw)

        return response

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
    try:
        funcourse = Course.objects.create(key=ck)
    except IntegrityError:
        funcourse = Course.objects.get(key=ck)
    if not funcourse.university:
        try:
            funcourse.university = University.objects.get(code=ck.org)
            funcourse.save()
        except University.DoesNotExist:
            messages.warning(request, _(u"University with code <strong>%s</strong> does not exist.") % ck.org)

    TeacherFormSet = inlineformset_factory(Course, Teacher, formset=FirstRequiredFormSet, can_delete=True)

    if request.method == 'POST':
        if request.POST['action'] == 'delete-course':
            # from xmodule.contentstore.utils.delete_course_and_groups function
            module_store = modulestore()
            with module_store.bulk_operations(ck):
                module_store.delete_course(ck, request.user.id)

            CourseAccessRole.objects.filter(course_id=ck).delete()  # shall we also delete student's enrollments ?
            funcourse.delete()
            messages.warning(request, _(u"Course <strong>%s</strong> has been deleted.") % course.course.id)
            log.warning('Course %s deleted by user %s', course.course.id, request.user.username)
            return redirect('backoffice:courses-list')

        elif request.POST['action'] == 'update-teachers':
            teacher_formset = TeacherFormSet(instance=funcourse, data=request.POST or None)
            if teacher_formset.is_valid():
                teacher_formset.save()

                messages.success(request, _(u"Teachers have been updated"))
                return redirect("backoffice:course-detail", course_key_string=course_key_string)

    try:
        university = University.objects.get(code=course.course.org)
    except University.DoesNotExist:
        university = None

    teacher_formset = TeacherFormSet(instance=funcourse)
    studio_url = get_cms_course_link(course.course)
    roles = CourseAccessRole.objects.filter(course_id=ck)

    return render(request, 'backoffice/course.html', {
            'course': course,
            'studio_url': studio_url,
            'teacher_formset': teacher_formset,
            'university': university,
            'roles': roles,

        })


@group_required('fun_backoffice')
def ora2_submissions(request, course_key_string):
    output_file = tempfile.NamedTemporaryFile(suffix=".tar.gz")
    OaCommand().dump_to(course_key_string, output_file.name)
    response = HttpResponse(open(output_file.name).read(), content_type='application/x-gzip')
    response['Content-Disposition'] = 'attachment; filename="openassessments.tar.gz"'
    return response
