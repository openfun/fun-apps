from django.http import HttpResponseForbidden

from django.conf import settings
from django.shortcuts import redirect
from static_template_view.views import render_404
from instructor.views.api import require_level

DEFAULT_AGREEMENT_FORM = "/payment/terms/"


def staff_required(func):
    """View decorator for staff members.

    Contrary to the corresponding django decorator, this decorator raises a 404
    error whenever a non-staff or non-active user tries to login.
    """
    def wrapped(request, *args, **kwargs):
        if request.user.is_active and request.user.is_staff:
            return func(request, *args, **kwargs)
        else:
            return render_404(request)
    return wrapped

def staff_required_or_level(level):
    """View decorator for staff or course member.

    View decorator that ensures that the requesting user is either an active
    staff member or an allowed member of the course staff. This decorator is
    mainly based on the require_level decorator from edx.
    Contrary to the require_level decorator, this decorator raises a 404 for
    every unauthorized access.
    """
    edx_decorator = require_level(level)
    def decorator(func):
        def wrapped(request, *args, **kwargs):
            if not request.user.is_active:
                return render_404(request)
            elif request.user.is_staff:
                return func(request, *args, **kwargs)
            else:
                response = edx_decorator(func)(request, *args, **kwargs)
                if isinstance(response, HttpResponseForbidden):
                    return render_404(request)
                else:
                    return response
        return wrapped
    return decorator
