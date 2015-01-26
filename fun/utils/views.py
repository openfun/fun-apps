from functools import wraps

from django.http import Http404, HttpResponseForbidden

from instructor.views.api import require_level
from static_template_view.views import render_404
from util.views import ensure_valid_course_key as edx_ensure_valid_course_key

def ensure_valid_course_key(view_func):
    """Render 404 template on invalid course key.

    This function is based on the eponymous function from edx in util.views. It
    addresses an issue in test: whenever an Http404 is raised in tests, the
    404.html template cannot be found and a TemplateDoesNotExist error is
    raised.
    """
    edx_inner = edx_ensure_valid_course_key(view_func)

    @wraps(view_func)
    def inner(request, *args, **kwargs):
        try:
            return edx_inner(request, *args, **kwargs)
        except Http404:
            return render_404(request)

    return inner

def staff_required_or_level(level):
    """View decorator for staff or course member.

    View decorator that ensures that the requesting user is either a staff
    member or an allowed member of the course staff. This decorator is mainly
    based on the require_level decorator from edx.
    Contrary to the require_level decorator, this decorator raises a 404 for
    every unauthorized access.
    """
    edx_decorator = require_level(level)
    def decorator(func):
        def wrapped(*args, **kwargs):
            request = args[0]
            if request.user.is_staff:
                return func(*args, **kwargs)
            else:
                response = edx_decorator(func)(*args, **kwargs)
                if isinstance(response, HttpResponseForbidden):
                    return render_404(request)
                else:
                    return response
        return wrapped
    return decorator
