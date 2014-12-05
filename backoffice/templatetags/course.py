# -*- coding: utf-8 -*-

from django import template
from django.template.defaultfilters import stringfilter

from courseware.courses import course_image_url, get_course_about_section

register = template.Library()

ABOUT_SECTION_FIELDS = ['title', 'university']

@register.assignment_tag
def course_infos(course):
    d = {}
    for section in ABOUT_SECTION_FIELDS:
        d[section] = get_course_about_section(course, section)
    d['course_image_url'] = course_image_url(course)
    return d
