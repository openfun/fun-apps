import csv
from datetime import datetime
from StringIO import StringIO

from django.http import HttpResponse, HttpResponseForbidden

from instructor.views.api import require_level
from static_template_view.views import render_404


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

def csv_response(header_row, data_rows, filename):
    def encode_data(data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, datetime):
            return data.strftime('%Y/%m/%d')
        else:
            return u"{}".format(data)

    response_content = StringIO()
    writer = csv.writer(response_content)
    writer.writerow([field.encode('utf-8') for field in header_row])
    for data_row in data_rows:
        writer.writerow([encode_data(d) for d in data_row])
    response_content.seek(0)

    response = HttpResponse(response_content.read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response