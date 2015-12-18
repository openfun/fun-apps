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


def dates_description(course):
    # As we do not know user timezone, assume he is in the same as instructor :-/
    FORMAT = '%d/%m/%Y'  # '%A %d %B %Y'

    now = timezone.make_aware(datetime.datetime.utcnow(), course.start.tzinfo)
    inscription_inverval = ''
    course_interval = ''
    if course.enrollment_start and course.enrollment_start > now:
        inscription_inverval = u"Inscription à partir du %s" % (course.enrollment_start.strftime(FORMAT))
    elif (course.enrollment_start and course.enrollment_end and
          course.enrollment_start < now and course.enrollment_end > now):
        inscription_inverval = u"Inscription jusqu'au %s" % (course.enrollment_end.strftime(FORMAT))
    else:
        inscription_inverval = u"Les inscriptions sont terminées"
    if course.start and course.start > now:
        if course.end:
            course_interval = u"Le cours dure du %s au %s" % (
                course.start.strftime(FORMAT), course.end.strftime(FORMAT)
            )
        else:
            course_interval = u"Le cours démarre le %s" % (course.start.strftime(FORMAT))
    elif course.end and course.end > now:
        course_interval = u"Le cours dure jusqu'au %s" %(course.end.strftime(FORMAT))
    else:
        course_interval = u"Le cours est terminé"

    course.inscription_inverval = inscription_inverval
    course.course_interval = course_interval
    return course


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