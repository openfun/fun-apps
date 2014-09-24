from opaque_keys.edx.locations import SlashSeparatedCourseKey
from instructor_task.models import ReportStore
from util.json_request import JsonResponse
from courseware.courses import get_course_with_access, get_course_by_id

from django_future.csrf import ensure_csrf_cookie
from django.views.decorators.cache import cache_control
from courseware.access import has_access

def require_level(level):
    """
    Decorator with argument that requires an access level of the requesting
    user. If the requirement is not satisfied, returns an
    HttpResponseForbidden (403).

    Assumes that request is in args[0].
    Assumes that course_id is in kwargs['course_id'].

    `level` is in ['instructor', 'staff']
    if `level` is 'staff', instructors will also be allowed, even
    if they are not in the staff group.
    """
    if level not in ['instructor', 'staff']:
        raise ValueError("unrecognized level '{}'".format(level))

    def decorator(func):  # pylint: disable=C0111
        def wrapped(*args, **kwargs):  # pylint: disable=C0111
            request = args[0]
            course = get_course_by_id(SlashSeparatedCourseKey.from_deprecated_string(kwargs['course_id']))

            if has_access(request.user, level, course):
                return func(*args, **kwargs)
            else:
                return HttpResponseForbidden()
        return wrapped
    return decorator


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@require_level('staff')
def list_report_downloads(_request, course_id):
    """
    List grade CSV files that are available for download for this course.
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

