# -*- coding: utf-8 -*-

import datetime
import re

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils import translation

from courseware.courses import get_courses, sort_by_announcement
from xmodule.contentstore.content import StaticContent

from .forms import CourseFilteringForm

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
    form = CourseFilteringForm(request.GET or None)
    by = request.GET.get('by', False)  # override default page size

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
    elif form.errors:
        return redirect(course_index)
    courses = _sort_courses(courses)

    # paginate courses
    paginator = Paginator(courses, by or COURSES_BY_PAGE, orphans=3)
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


def get_dmcloud_url(course, video_id):
    '''Build the dmcloud url from the video_id and return the html snippet'''
    if len(video_id) > 20:
        # Studio saves in mongo youtube urls with dmcloud id, we have to extract dmclouid to build correct url
        try:
            dmcloud = re.compile('/([\d\w]+)\?').search(video_id).groups()[0]
        except AttributeError:
            dmcloud = ''
    else:
        # FUN v1 did the stuff write
        dmcloud = video_id
    html='<iframe width="560" height="315" frameborder="0" scrolling="no" allowfullscreen="" src="//www.dailymotion.com/embed/video/' + dmcloud + '"></iframe>'
    return html


def course_image_url(course, image_name=None):
    """Return url for image_name or default course image in given course assets.
    """
    image = image_name or course.course_image
    loc = StaticContent.compute_location(course.location.course_key, image)
    path = loc.to_deprecated_string()
    return path
