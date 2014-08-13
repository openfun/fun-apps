# -*- coding: utf-8 -*-

import datetime

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.utils import translation

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from courseware.courses import get_courses, sort_by_announcement

from .forms import CourseFileteringForm


COURSES_BY_PAGE = 2


def _dates_description(course):
    #import ipdb; ipdb.set_trace()
    # As we do not know user timezone, assume he is in the same as instructor :-/
    FORMAT = '%A %d %B %Y'
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


def _sort_courses(courses):
    """Sort courses in a usefull order for user:
        - courses with enrollement date started should be first
        - then course to start to enroll should be ordered by enrollement start date (asc)
        - then course which started should be sorted by days to go (desc) or by start date asc
        - then courses ended by end data (asc)
    """

    def _sort_by_novelty(a, b):
        # quick and dirty implementation wich probably works in most easy cases
        if a.enrollment_start and b.enrollment_start:
            return a.enrollment_start < b.enrollment_start
        elif a.enrollment_start and not b.enrollment_start:
            return True
        else:
            return a.start < b.start
    return sorted(courses, _sort_by_novelty)

def course_index(request):
    #courses = get_courses(request.user)
    courses = [_dates_description(course) for course in get_courses(request.user)]
    courses = _sort_courses(courses)

    form = CourseFileteringForm(request.GET or None)

    # paginate courses
    paginator = Paginator(courses, COURSES_BY_PAGE, orphans=0)
    page = request.GET.get('page')

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    #request.LANGUAGE_CODE = translation.get_language()

    return render(request, 'courses/index.html', {
        'form': form,
        'courses': courses,
        'current_language': translation.get_language(),
    })



#CourseKey.from_string('rm/003/now')
# course_module = modulestore().get_course(key, depth=0)

#from opaque_keys.edx.keys import CourseKey
#from xmodule.modulestore.django import modulestore
#from course_metadata import CourseMetadata  # from cms.models.settings
#
#def _get_course_module(course_key, user, depth=0):
#    """
#    Internal method used to calculate and return the locator and course module
#    for the view functions in this file.
#    """
#    if not has_course_access(user, course_key):
#        raise PermissionDenied()
#    course_module = modulestore().get_course(course_key, depth=depth)
#    return course_module
#
#
#course_key = CourseKey.from_string(course_key_string)
#course_module = _get_course_module(course_key, request.user)