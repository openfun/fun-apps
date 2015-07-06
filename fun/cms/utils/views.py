from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import Http404

from opaque_keys import InvalidKeyError
from opaque_keys.edx.keys import CourseKey
import student.auth

def has_write_access_to_course(view_func):
    """View decorator to check user is logged in and accessing a proper course for which he has write access.

    This decorator is for view of the form `def myview(request, course_key_string, ...)`.
    """
    @wraps(view_func)
    def wrapped(request, course_key_string, *args, **kwargs):
        # 2) Check course exists
        try:
            course_key = CourseKey.from_string(course_key_string)
        except InvalidKeyError:
            raise Http404()
        # 3) Check user has write access to course
        if not student.auth.has_studio_write_access(request.user, course_key):
            raise PermissionDenied()
        return view_func(request, course_key_string, *args, **kwargs)
    # 1) Check user is logged-in
    return login_required()(wrapped)
