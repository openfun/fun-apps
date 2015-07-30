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
