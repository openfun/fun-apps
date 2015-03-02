from django.contrib.auth.decorators import user_passes_test

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

def get_course(course_key_string):
    """
    Return the edX course object  for a given course_key.
    """
    ck = get_course_key(course_key_string)
    course = modulestore().get_course(ck, depth=0)
    return course

def get_course_key(course_key_string):
    """
    Return the edX course object  for a given course_key.
    """
    ck = CourseKey.from_string(course_key_string)
    return ck

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated():
            if bool(u.groups.filter(name__in=group_names)) or u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups)
