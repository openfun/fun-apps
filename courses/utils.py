# -*- coding: utf-8 -*-

import datetime
import re

from django.utils import timezone

from courseware.courses import sort_by_announcement
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import ItemNotFoundError


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


def get_dmcloud_url(course, video_id):
    '''Build the dmcloud url from the video_id and return the html snippet'''
    if len(video_id) > 20:
        # Studio saves in mongo youtube urls with dmcloud id, we have to extract dmclouid to build correct url
        try:
            dmcloud = re.compile(r'/([\d\w]+)\?').search(video_id).groups()[0]
        except AttributeError:
            dmcloud = ''
    else:
        # FUN v1 did the stuff write
        dmcloud = video_id
    html = ('<iframe width="560" height="315" frameborder="0" '
            'scrolling="no" allowfullscreen="" src="//www.dailymotion.com/embed/video/') + dmcloud + '"></iframe>'
    return html


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


def registration_datetime_text(course, date):
    """Returns the registration date for the course formatted as a string."""

    strftime = course.runtime.service(course, "i18n").strftime
    date_time = strftime(date, "SHORT_DATE")
    return date_time
