# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone

from courseware.courses import get_courses, sort_by_announcement

from .forms import CourseFileteringForm


def _dates_description(course):
    #import ipdb; ipdb.set_trace()
    # As we do not know user timezone, assume he is in the same as instructor :-/
    FORMAT = '%A %d %B'
    now = timezone.make_aware(datetime.datetime.utcnow(), course.start.tzinfo)
    inscription_inverval = ''
    course_interval = ''
    if course.enrollment_start and course.enrollment_start > now:
        inscription_inverval = u"Inscription à partir du %s" % (course.enrollment_start.strftime(FORMAT))
    elif course.enrollment_start and course.enrollment_start < now and course.enrollment_end > now:
        inscription_inverval = u"Inscription jusqu'au du %s" % (course.enrollment_end.strftime(FORMAT))
    else:
        inscription_inverval = u"Les inscription sont terminées"
    if course.start and course.start > now:
        if course.end:
            course_interval = u"Le cours dur du %s au %s" % (course.start.strftime(FORMAT), course.end.strftime(FORMAT))
        else:
            course_interval = u"Le cours démarre le %s" % (course.start.strftime(FORMAT))
    elif course.end and course.end < now:
        course_interval = u"Le cours dur jusqu'au %s" %(course.end.strftime(FORMAT))

    course.inscription_inverval = inscription_inverval
    course.course_interval = course_interval
    return course


def course_index(request):
    #courses = get_courses(request.user)
    courses = [_dates_description(course) for course in get_courses(request.user)]
    form = CourseFileteringForm(request.GET or None)

    return render(request, 'courses/index.html', {
        'form': form,
        'courses': courses,

    })

