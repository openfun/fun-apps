# -*- coding: utf-8 -*-

import re

from django.conf import settings
from django.http import Http404

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore


def is_cms_running():
    """Return True if we are running the cms service variant"""
    return settings.ROOT_URLCONF == 'fun.cms.urls'


def is_lms_running():
    """Return True if we are running the lms service variant"""
    return settings.ROOT_URLCONF == 'fun.lms.urls'


def get_course(course_key_string):
    """Return the course module associated to a string ID."""
    course_key = CourseKey.from_string(course_key_string)
    return modulestore().get_course(course_key)


def get_fun_course(course):
    """Return the fun-app.courses.models.Course from edX course key."""
    from courses.models import Course
    try:
        return Course.objects.get(key=course.id.to_deprecated_string(), show_in_catalog=True)
    except Course.DoesNotExist:
        # We want to reply 404 to attempt to access syllabus of course not yet published (show_in_catalog)
        # But this should be handled by edx view lms/djangoapps/courseware/views.py@course_about
        raise Http404


def get_teaser(video_id):
    """Build the DailyMotion url from the video_id and return the html snippet.

    The teaser will be an HTML5 video that will auto-play.

    Args:
        video_id (str)
    """
    if len(video_id) > 20:
        # Studio saves in Mongo a Youtube urls with DailyMotion ID,
        # we have to extract DailyMotion ID to build correct url
        try:
            dm_id = re.compile(r'/([\d\w]+)\?').search(video_id).groups()[0]
        except AttributeError:
            dm_id = ''
    else:
        # FUN v1 did the stuff right
        dm_id = video_id

    return (
        '<iframe id="course-teaser" '
        'frameborder="0" scrolling="no" allowfullscreen="" '
        'src="//www.dailymotion.com/embed/video/{dm_id}/?html=1&autoplay=1"'
        '></iframe>'
    ).format(dm_id=dm_id)


def registration_datetime_text(course, date):
    """Returns the registration date for the course formatted as a string."""

    strftime = course.runtime.service(course, "i18n").strftime
    date_time = strftime(date, "SHORT_DATE")
    return date_time
