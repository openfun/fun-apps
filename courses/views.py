# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.utils import translation

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from courseware.courses import get_courses, sort_by_announcement

from .forms import CourseFileteringForm


COURSES_BY_PAGE = 12


def _dates_description(course):
    # As we do not know user timezone, assume he is in the same as instructor :-/
    FORMAT = '%d/%m/%Y'  # '%A %d %B %Y'

    now = timezone.make_aware(datetime.datetime.utcnow(), course.start.tzinfo)
    inscription_inverval = ''
    course_interval = ''
    if course.enrollment_start and course.enrollment_start > now:
        inscription_inverval = u"Inscription à partir du %s" % (course.enrollment_start.strftime(FORMAT))
    elif course.enrollment_start and course.enrollment_end and course.enrollment_start < now and course.enrollment_end > now:
        inscription_inverval = u"Inscription jusqu'au du %s" % (course.enrollment_end.strftime(FORMAT))
    else:
        inscription_inverval = u"Les inscriptions sont terminées"
    if course.start and course.start > now:
        if course.end:
            course_interval = u"Le cours dure du %s au %s" % (course.start.strftime(FORMAT), course.end.strftime(FORMAT))
        else:
            course_interval = u"Le cours démarre le %s" % (course.start.strftime(FORMAT))
    elif course.end and course.end > now:
        course_interval = u"Le cours dure jusqu'au %s" %(course.end.strftime(FORMAT))
    else:
        course_interval = u"Le cours est terminé"

    course.inscription_inverval = inscription_inverval
    course.course_interval = course_interval
    return course


def _sort_courses(courses):
    """Sort courses in a usefull order for user:
        - courses with enrollement date started should be first
        - then course to start to enroll should be ordered by enrollement start date (asc)
        - then course which started should be sorted by days to go (desc) or by start date asc
        - then courses ended by end data (asc)
    We also should try sort_by_announcement order
    """

    def _sort_by_novelty(a, b):
        # quick and dirty implementation wich probably works in most easy cases
        if a.enrollment_start and b.enrollment_start:
            return a.enrollment_start < b.enrollment_start
        elif a.enrollment_start and not b.enrollment_start:
            return True
        else:
            return a.start < b.start
    return sort_by_announcement(courses)  # sorted(courses, _sort_by_novelty)


def course_index(request):
    courses = [_dates_description(course) for course in get_courses(request.user)]
    form = CourseFileteringForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data['university']:
            courses = [c for c in courses if c.org == form.cleaned_data['university']]
        if form.cleaned_data['state']:
            now = timezone.make_aware(datetime.datetime.utcnow(), timezone.get_current_timezone())
            if form.cleaned_data['state'] == 'future':
                courses = [c for c in courses if c.start and c.start > now]
            elif form.cleaned_data['state'] == 'current':
                courses = [c for c in courses if c.start and c.start < now and c.end and c.end > now]
            elif form.cleaned_data['state'] == 'past':
                courses = [c for c in courses if c.end and c.end < now]

    courses = _sort_courses(courses)

    # paginate courses
    paginator = Paginator(courses, COURSES_BY_PAGE, orphans=3)
    page = request.GET.get('page')

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)


    return render(request, 'courses/index.html', {
        'form': form,
        'courses': courses,
        'current_language': translation.get_language(),
    })
