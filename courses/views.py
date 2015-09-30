# -*- coding: utf-8 -*-

import datetime

from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from courseware.courses import get_courses, get_course_about_section

from universities.models import University

from . import utils as courses_utils


class CourseIndexView(TemplateView):
    template_name = 'courses/index.html'


class CoursesFeed(Feed):
    title = _(u"Fun latest published courses")
    link = "/cours/feed/"
    description = _(u"Latests courses published on www.france-universite-numerique-mooc.fr")
    __name__ = 'FUNRSS'

    def items(self, request):
        return courses_utils.sort_courses(get_courses(None))[:16]

    def item_title(self, course):
        return get_course_about_section(course, 'title')

    def item_description(self, course):
        course = courses_utils.dates_description(course)
        context = {}
        context['image_url'] = courses_utils.course_image_url(course) + '?width=300'
        context['short_description'] = get_course_about_section(course, 'short_description')
        context['course'] = course
        try:
            context['university'] = University.objects.get(code=course.org)
        except University.DoesNotExist:
            pass
        return render_to_string('courses/feed/feed.html', context)

    def item_link(self, course):
        return reverse('about_course', args=[course.id.to_deprecated_string()])


courses_index = CourseIndexView.as_view()
