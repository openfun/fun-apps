# -*- coding: utf-8 -*-

from collections import defaultdict

from django.conf import settings
from django.contrib.auth import load_backend, BACKEND_SESSION_KEY
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from django.http import Http404

from pure_pagination import Paginator, PageNotAnInteger

from course_modes.models import CourseMode
from microsite_configuration import microsite
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, UserSignupSource
from xmodule.modulestore.django import modulestore


def get_course(course_key_string):
    """
    Return the edX course object for a given course key, passed as string.
    """
    ck = get_course_key(course_key_string)
    course = modulestore().get_course(ck, depth=0)
    return course

def get_course_key(course_key_string):
    """
    Return the edX CourseKey object for a given course key, passed as string.

    Args:
        course_key_string (str)
    Returns:
        course_key (CourseKey)
    """
    return CourseKey.from_string(course_key_string)

def group_required(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(user):
        if user.is_authenticated():
            if (
                    user.is_superuser or
                    bool(user.groups.filter(name__in=group_names))):
                if settings.FEATURES['USE_MICROSITES']:
                    return UserSignupSource.objects.filter(user=user,
                            site=microsite.get_value('SITE_NAME')).exists()
                return True
            else:
                # 403 errors are not properly handled. As a consequence, we
                # prefer to display a 404 page.
                raise Http404()
        # Redirect to login page
        return False

    return user_passes_test(in_groups)


LIMIT_BY_PAGE = 100

def order_and_paginate_queryset(request, queryset, default_order):
    order = request.GET.get('order', default_order)
    direction = '-' if 'd' in request.GET else ''
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    queryset = queryset.order_by(direction + order)
    paginator = Paginator(queryset, LIMIT_BY_PAGE, request=request)
    return paginator.page(page)


def get_course_modes():
    """Returns a dict of existing course modes:
        {'org/session/number': ['verified', 'honor'],}
    """
    modes = CourseMode.objects.all()
    course_modes = defaultdict(list)
    for mode in modes:
        course_modes[unicode(mode.course_id)].append(mode.mode_slug)
    return course_modes


def get_enrollment_mode_count(course_key):
    """Returns dict of enrollments counts for modes if course has modes else empty dict.
        {'honor': 12, 'verified: 0'}

    """
    course_modes = get_course_modes()  # retrieve all course modes
    if course_modes[unicode(course_key)]:
        # count enrollments for each course mode for given course (this will NOT find mode with 0 enrollments)
        enrollments = {enrollment['mode']: enrollment['count']
                for enrollment in CourseEnrollment.objects.filter(course_id=course_key
                ).values('mode').annotate(count=Count('id'))}

    # build convenient dict like {'honor': 12, 'verified': 0}
    mode_count = {}
    for mode in course_modes[unicode(course_key)]:
        mode_count[mode] = enrollments[mode] if mode in enrollments else 0

    return mode_count


def get_used_backend(request):
    backend_str = request.session[BACKEND_SESSION_KEY]
    backend = load_backend(backend_str)
    return backend
