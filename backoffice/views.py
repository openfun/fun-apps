# -*- coding: utf-8 -*-

import datetime
import random
import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.forms.formsets import formset_factory

from courseware.courses import get_courses, sort_by_announcement
from courseware.courses import course_image_url, get_course_about_section
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from capa.xqueue_interface import make_hashkey

from backoffice.forms import StudentCertificateForm, TeachersCertificateForm, RequiredFormSet
from fun_certificates.generator import CertificateInfo
from universities.models import University

ABOUT_SECTION_FIELDS = ['title', 'university']

from django.contrib.auth.decorators import user_passes_test


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
    setattr(course, 'ident', course.id.to_deprecated_string())

    return course


@group_required('fun_backoffice')
def courses_list(request):
    courses = get_courses(request.user)

    courses = [course_infos(course) for course in courses]
    pattern = request.GET.get('search')

    if pattern:
        courses = [course for course in courses if pattern in course.title or pattern in course.ident]

    return render(request, 'backoffice/courses.html', {
        'courses': courses,
        'pattern': pattern,
    })


@group_required('fun_backoffice')
def course_detail(request, course_key_string):
    ck = CourseKey.from_string(course_key_string)
    course = modulestore().get_course(ck, depth=0)
    setattr(course, 'ident', course.id.to_deprecated_string())

    teachers_form_set = formset_factory(TeachersCertificateForm,
                                      extra=TeachersCertificateForm.MAX_TEACHERS,
                                      formset=RequiredFormSet)
    student_form = StudentCertificateForm()

    if request.method == 'POST':
        student_form = StudentCertificateForm(request.POST)
        teachers_form_set = teachers_form_set(request.POST)
        if (student_form.is_valid() and teachers_form_set.is_valid()):
            try:
                university = University.objects.get(code=course.org)
            except:
                messages.warning(request, _("University doesn't exist"))
            certificate = generate_test_certificate(course, university, student_form, teachers_form_set)
            if certificate:
                response = HttpResponse("", content_type='text/pdf')
                response['Content-Disposition'] = 'attachment; filename="{}"'.format(certificate.filename)
                with open(certificate.pdf_file_name, 'r') as gradefile:
                    response.write(gradefile.read())
                return response
            else:
                messages.error(request, _('Certificated generation failed'))

    return render(request, 'backoffice/course.html', {
            'course': course,
            'student_form_certificate' : student_form,
            'teachers_form_certificate' : teachers_form_set,
        })

def generate_test_certificate(course, university, student_form, teachers_form_set):
    """Generate the pdf certicate, save it on disk"""

    certificate = CertificateInfo()

    certificate.full_name = student_form.cleaned_data['full_name']
    certificate.course_name = course.display_name
    certificate.organization = course.org

    # make a teachers/title list from the teachers_form_set
    certificate.teachers =  [u"{}/{}".format(teacher.cleaned_data['full_name'],
                                            teacher.cleaned_data['title'],)  for teacher in teachers_form_set
                             if 'full_name'  in teacher.cleaned_data and 'title' in teacher.cleaned_data]

    if university.certificate_logo:
        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
    certificate.organization_logo = logo_path

    key = make_hashkey(random.random())
    certificate.filename = "TEST_attestation_suivi_%s_%s.pdf" % (
            course.id.to_deprecated_string().replace('/','_'), key)
    certificate.pdf_file_name = os.path.join(
        settings.CERTIFICATES_DIRECTORY, certificate.filename)

    if certificate.generate():
        return certificate
    else:
        return False


