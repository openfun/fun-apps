# -*- coding: utf-8 -*-

import datetime

from django.db.models import Count
from django.utils import timezone

from courseware.courses import sort_by_announcement
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError

from .choices import COURSE_LANGUAGES
from .models import Course


def get_about_section(course_descriptor, field):
    """
    Faster alternative to courseware.courses.get_course_about_section.
    Returns None if the key does not exist.
    """
    usage_key = course_descriptor.id.make_usage_key("about", field)
    try:
        return modulestore().get_item(usage_key).data
    except ItemNotFoundError:
        return None


def sort_courses(courses):
    """Sort courses in a usefull order for user:
        - courses with enrollement date started should be first
        - then course to start to enroll should be ordered by enrollement start date (asc)
        - then course which started should be sorted by days to go (desc) or by start date asc
        - then courses ended by end data (asc)
    We also should try sort_by_announcement order
    """

    def _sort_by_novelty(a, b):
        # quick and dirty implementation wich probably works in most easy cases
        if a.enrollment_start and b.enrollment_start:
            return a.enrollment_start < b.enrollment_start
        elif a.enrollment_start and not b.enrollment_start:
            return True
        else:
            return a.start < b.start
    return sort_by_announcement(courses)  # sorted(courses, _sort_by_novelty)


def course_image_url(course, image_name=None):
    """Return url for image_name or default course image in given course assets.
    It allows us to override default course image in templates when this function is
    used whith image_name parameter, if the image is available. (see course_about.html)
    """
    image = image_name or course.course_image
    try:
        loc = StaticContent.compute_location(course.location.course_key, image)
        _ = contentstore().find(loc)
    except NotFoundError:
        loc = StaticContent.compute_location(course.location.course_key, course.course_image)

    return loc.to_deprecated_string()


def get_courses_per_language():
    """Returns available languages for courses from constant COURSE_LANGUAGES,
       count of public courses of thoses language and the i18ned name of the language.

       Returns: list of dicts
    """
    # retrieve authorized course languages
    course_languages = [language[0] for language in COURSE_LANGUAGES]
    # get course count for distinct languages
    languages = Course.objects.public().filter(language__in=course_languages
            ).values('language').distinct().annotate(count=Count('id'))
    # update returned dict with language name comming from courses.choices.COURSE_LANGUAGES
    languages = [dict(language, title=unicode(dict(COURSE_LANGUAGES)[language['language']])) for language in languages]
    return languages