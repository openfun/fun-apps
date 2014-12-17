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

from courseware.courses import get_courses, sort_by_announcement
from courseware.courses import course_image_url, get_course_about_section
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore
from capa.xqueue_interface import make_hashkey

from backoffice.forms import TestCertificateForm
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

    if request.method == 'POST':
        form = TestCertificateForm(request.POST)
        if (form.is_valid()):
            return generate_test_certificate(request, course, form)
    else:
        form = TestCertificateForm()
    return render(request, 'backoffice/course.html', {
        'course': course,
        'form' : form,
    })

def generate_test_certificate(request, course, form):
    """Generate the pdf certicate, save it on disk and then return the certificate as http response"""

    try:
        university = University.objects.get(code=course.org)
    except:
        messages.warning(request, _("University doesn't exist"))
        return redirect(reverse('backoffice-course-detail', args=[course.id.to_deprecated_string()]))

    if university.certificate_logo:
        logo_path = os.path.join(university.certificate_logo.url, university.certificate_logo.path)
    else:
        logo_path = None

    certificate = CertificateInfo()

    certificate.full_name = form.cleaned_data['full_name']
    certificate.course_name = course.display_name
    certificate.organization = course.org
    certificate.teachers = form.make_teachers_list()
    certificate.organization_logo = logo_path

    key = make_hashkey(random.random())
    certificate_filename = "TEST_attestation_suivi_%s_%s.pdf" % (
            course.id.to_deprecated_string().replace('/','_'), key)
    certificate.pdf_file_name = os.path.join(
        settings.CERTIFICATES_DIRECTORY, certificate_filename)
    if certificate.generate():
        response = HttpResponse("", content_type='text/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(certificate_filename)
        with open(certificate.pdf_file_name, 'r') as gradefile:
            response.write(gradefile.read())
        return (response)
    else:
        messages.error(request, _('Certificated generation failed'))
        return redirect(reverse("backoffice-course-detail", args=[course.id.to_deprecated_string()]))

