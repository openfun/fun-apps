from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

def get_course(course_key_string):
    """
    Return the edX course object  for a given course_key.
    """
    ck = CourseKey.from_string(course_key_string)
    course = modulestore().get_course(ck, depth=0)
    return course

def get_course_key(course_key_string):
    """
    Return the edX course object  for a given course_key.
    """
    ck = CourseKey.from_string(course_key_string)
    return ck

