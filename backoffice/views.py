# -*- coding: utf-8 -*-

import logging
import os
import json
import random

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.db.utils import IntegrityError
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext_lazy as _

from courseware.courses import course_image_url, get_course_about_section, get_courses, get_cms_course_link
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole
from xmodule.modulestore.django import modulestore

from backoffice.forms import StudentCertificateForm, FirstRequiredFormSet
from backoffice.utils import get_course

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
    try:
        funcourse = Course.objects.create(key=ck)
    except IntegrityError:
        funcourse = Course.objects.get(key=ck)
    if not funcourse.university:
        try:
            funcourse.university = University.objects.get(slug=ck.org)
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
            messages.warning(request, _(u"Course <strong>%s</strong> has been deleted.") % course.id)
            log.warning('Course %s deleted by user %s' % (course.id, request.user.username))
            return redirect(courses_list)

        elif request.POST['action'] == 'update-teachers':


            teacher_formset = TeacherFormSet(instance=funcourse, data=request.POST or None)
            if teacher_formset.is_valid():
                teacher_formset.save()

                messages.success(request, _(u"Teachers have been updated"))
                return redirect(course_detail, course_key_string=course_key_string)

    try:
        university = University.objects.get(code=course.org)
    except University.DoesNotExist:
        university = None

    teacher_formset = TeacherFormSet(instance=funcourse)
    studio_url = get_cms_course_link(course)
    roles = CourseAccessRole.objects.filter(course_id=ck)

    return render(request, 'backoffice/course.html', {
            'course': course,
            'studio_url': studio_url,
            'teacher_formset': teacher_formset,
            'university': university,
            'roles': roles,
        })