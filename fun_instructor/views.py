# -*- coding: utf-8 -*-

from util.json_request import JsonResponse

from django_future.csrf import ensure_csrf_cookie
from django.views.decorators.cache import cache_control

from opaque_keys.edx.locations import SlashSeparatedCourseKey

from courseware.courses import get_course_with_access, get_course_by_id
from courseware.access import has_access
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
            dict(name=name, url=url.replace('file:///tmp/edx-s3', "") , link='<a href="{}">{}</a>'.format(url.replace('file:///tmp/edx-s3', ""), name))
            for name, url in report_store.links_for(course_id)
        ]
    }
    return JsonResponse(response_payload)

