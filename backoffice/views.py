# -*- coding: utf-8 -*-

import datetime

from django.shortcuts import render, redirect

from courseware.courses import get_courses, sort_by_announcement
from courseware.courses import course_image_url, get_course_about_section
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


ABOUT_SECTION_FIELDS = ['title', 'university']


def course_infos(course):
    for section in ABOUT_SECTION_FIELDS:
        setattr(course, section, get_course_about_section(course, section))
    setattr(course, 'course_image_url', course_image_url(course))
    setattr(course, 'ident', course.id.to_deprecated_string())

    return course


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


def course_detail(request, course_key_string):
    ck = CourseKey.from_string(course_key_string)
    course = modulestore().get_course(ck, depth=0)


    return render(request, 'backoffice/course.html', {
        'course': course,
    })
