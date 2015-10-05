# -*- coding: utf-8 -*-

import re

from django.conf import settings

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
    return Course.objects.get(key=course.id.to_deprecated_string())

def get_teaser(course, video_id, autoplay=True):
    """Build the DailyMotion url from the video_id and return the html snippet"""
    if len(video_id) > 20:
        # Studio saves in mongo youtube urls with dmcloud id, we have to extract dmclouid to build correct url
        try:
            dm_id = re.compile(r'/([\d\w]+)\?').search(video_id).groups()[0]
        except AttributeError:
            dm_id = ''
    else:
        # FUN v1 did the stuff right
        dm_id = video_id
    html = '<iframe frameborder="0" scrolling="no" allowfullscreen="" src="//www.dailymotion.com/embed/video/%s/?autoplay=%d"></iframe>' % (
            dm_id, int(autoplay))
    return html
