# -*- coding: utf-8 -*-

from util.json_request import JsonResponse
import urllib
import os

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import Http404
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from django.conf import settings

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from instructor.views.api import require_level
from instructor_task.models import ReportStore

@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@require_level('staff')
def list_report_downloads(_request, course_id):
    """
    List grade CSV files that are available for download for this course.
    Remove  "file:///tmp/edx-s3" from the url to permit download
    """

    course_id = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    report_store = ReportStore.from_config()

    response_payload = {
        'downloads': [
            dict(name=name,
                 url='/get-grades/{}/{}'.format(course_id.to_deprecated_string(), name),
                 link='<a href="{}">{}</a>'.format(url, name)
             )
            for name, url in report_store.links_for(course_id)
        ]
    }
    return JsonResponse(response_payload)


def path_to(course_id, filename):
    """Return the full path to a given file for a given course."""

    return os.path.join(settings.GRADES_DOWNLOAD['ROOT_PATH'], urllib.quote(course_id, safe=''), filename)


@require_level('staff')
def get_grades(_request, course_id, filename):
    """
    This function will return the grade report asked from the instructor dashboard
    """

    # tell the browser to treat the response as a file attachment
    response = HttpResponse("", content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

    # open the file and write its content into the http response
    # edx path to file are stored using urlib.quote() function on course_id
    # see store method in class LocalFSReportStore
    try:
        with open(path_to(course_id, filename), 'r') as gradefile:
            response.write(gradefile.read())
    except IOError:
        raise Http404("Report grades file was not found")
    return response


