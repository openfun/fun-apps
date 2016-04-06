# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test

from microsite_configuration import microsite
from opaque_keys.edx.keys import CourseKey
from student.models import UserSignupSource
from xmodule.modulestore.django import modulestore


def get_course(course_key_string):
    """
    Return the edX course object for a given course key, passed as string.
    """
    ck = get_course_key(course_key_string)
    course = modulestore().get_course(ck, depth=0)
    return course

def get_course_key(course_key_string):
    """
    Return the edX CourseKey object for a given course key, passed as string.

    Args:
        course_key_string (str)
    Returns:
        course_key (CourseKey)
    """
    return CourseKey.from_string(course_key_string)

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(user):
        if user.is_authenticated():
            if bool(user.groups.filter(name__in=group_names)) or user.is_superuser:
                if settings.FEATURES['USE_MICROSITES']:
                    return UserSignupSource.objects.filter(user=user,
                            site=microsite.get_value('SITE_NAME')).exists()
                return True
        return False
    return user_passes_test(in_groups)
