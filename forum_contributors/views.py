# -*- coding: utf-8 -*-

from django_future.csrf import ensure_csrf_cookie
from django.http import HttpResponseBadRequest
from django.utils.html import strip_tags
from django.views.decorators.cache import cache_control

from courseware.access import has_access
from courseware.courses import get_course_by_id
from django_comment_client.utils import has_forum_access
from django_comment_common.models import Role, FORUM_ROLE_ADMINISTRATOR
from instructor.access import update_forum_role
from instructor.views.api import require_level, require_query_params
from instructor.views.tools import get_student_from_identifier
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from util.json_request import JsonResponse


FORUM_ROLE_OFFICIAL_CONTRIBUTOR = 'Official Contributor'
FORUM_ROLE_RECOMMENDED = 'Recommended'
FORUM_ROLE_ACTIVE = 'Active'

CUSTOM_ROLES = [FORUM_ROLE_OFFICIAL_CONTRIBUTOR, FORUM_ROLE_RECOMMENDED, FORUM_ROLE_ACTIVE]

FIELDS = ['username', 'email', 'first_name', 'last_name']  # fields to serialize and return to ajax call


class UnauthorizedAccessError(Exception):
    pass

def _check_rights(course_id, user, rolename):
    """Check if user has correct rights."""
    course_id = SlashSeparatedCourseKey.from_deprecated_string(course_id)
    course = get_course_by_id(course_id)
    has_instructor_access = has_access(user, 'instructor', course)
    has_forum_admin = has_forum_access(user, course_id, FORUM_ROLE_ADMINISTRATOR)

    # default roles require either (staff & forum admin) or (instructor)
    if not (has_forum_admin or has_instructor_access):
        raise UnauthorizedAccessError(
            "Operation requires staff & forum admin or instructor access"
        )

    # filter out unsupported for roles
    if not rolename in CUSTOM_ROLES:
        raise UnauthorizedAccessError(strip_tags(
            "Unrecognized FUN special rolename '{}'.".format(rolename)
        ))

    return course_id


def _check_custom_roles(course_id):
    """Check the existence of our custom role for a given course.
    Create them if they do not.
    As our custom roles can not be added by django_comment_common.utils.seed_permissions_roles
    function at course creation, we have to create them on demand."""
    created = False
    for rolename in CUSTOM_ROLES:
        try:
            Role.objects.get(name=rolename, course_id=course_id)
            return created  # break at the first found
        except Role.DoesNotExist:
            Role.objects.create(name=rolename, course_id=course_id)
            created = True

    return created


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@require_level('staff')
@require_query_params('rolename')
def list_special_forum_contributors(request, course_id):

    rolename = request.GET.get('rolename')
    try:
        course_key = _check_rights(course_id, request.user, rolename)
    except UnauthorizedAccessError as e:
        return HttpResponseBadRequest(e.message)
    try:
        role = Role.objects.get(name=rolename, course_id=course_key)
        users = list(role.users.all().values(*FIELDS).order_by('username'))
    except Role.DoesNotExist:
        users = []

    response_payload = {
        'course_id': course_key.to_deprecated_string(),
        rolename: users,
    }
    return JsonResponse(response_payload)


@ensure_csrf_cookie
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@require_level('staff')
@require_query_params('rolename')
def modify_special_forum_contributors(request, course_id):

    unique_student_identifier = request.GET.get('unique_student_identifier')
    rolename = request.GET.get('rolename')
    action = request.GET.get('action')

    try:
        course_id = _check_rights(course_id, request.user, rolename)
    except UnauthorizedAccessError as e:
        return HttpResponseBadRequest(e.message)
    course = get_course_by_id(course_id)
    _check_custom_roles(course_id)

    user = get_student_from_identifier(unique_student_identifier)
    target_is_instructor = has_access(user, 'instructor', course)
    # cannot revoke instructor
    if target_is_instructor and action == 'revoke' and rolename == FORUM_ROLE_ADMINISTRATOR:
        return HttpResponseBadRequest("Cannot revoke instructor forum admin privileges.")
    try:
        update_forum_role(course_id, user, rolename, action)
    except Role.DoesNotExist:
        return HttpResponseBadRequest("Role does not exist.")

    response_payload = {
        'course_id': course_id.to_deprecated_string(),
        'action': action,
    }
    return JsonResponse(response_payload)
