# -*- coding: utf-8 -*-

from django import template

from courseware.courses import course_image_url
from courses.utils import get_about_section

register = template.Library()


@register.assignment_tag
def course_infos(course):
    d = {
        'course_image_url': course_image_url(course)
    }
    for section in ['title', 'university']:
        d[section] = get_about_section(course, section)
    return d
