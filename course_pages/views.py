# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.template.loader import render_to_string
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.translation import ugettext_lazy as _

from edxmako.shortcuts import render_to_response

from universities.models import University

from courses.models import Course, CourseSubject
from courses.managers import annotate_with_public_courses
from courses.utils import get_courses_per_language


def courses_index(request, subject=None):
    """
    Args:
        subject (str): subject slug that allows to reverse course filtering urls.
    """
    languages = get_courses_per_language()
    return render_to_response('course_pages/index.html', {
        "course_subjects": annotate_with_public_courses(CourseSubject.objects.by_score()),
        "universities": annotate_with_public_courses(University.objects.not_obsolete().by_score()),
        "languages": languages,
        "courses_count_start_soon": Course.objects.start_soon().count(),
        "courses_count_enrollment_ends_soon": Course.objects.enrollment_ends_soon().count(),
        "courses_count_new": Course.objects.new().count(),
        "courses_count_current": Course.objects.current().count(),
    })
