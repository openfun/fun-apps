# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from courseware.courses import get_courses, get_course_about_section
from edxmako.shortcuts import render_to_response

from universities.models import University

from courses.models import Course, CourseSubject
from courses.managers import annotate_with_public_courses
from courses.choices import COURSE_LANGUAGES
import courses.utils


def courses_index(request, subject=None):
    """
    Args:
        subject (str): subject slug that allows to reverse course filtering urls.
    """
    languages = courses.utils.get_courses_per_language()
    return render_to_response('course_pages/index.html', {
        "course_subjects": annotate_with_public_courses(CourseSubject.objects.by_score()),
        "universities": annotate_with_public_courses(University.objects.active_by_score()),
        "languages": languages,
        "courses_count_start_soon": Course.objects.start_soon().count(),
        "courses_count_end_soon": Course.objects.end_soon().count(),
        "courses_count_new": Course.objects.new().count(),
    })


class CoursesFeed(Feed):
    title = _(u"Fun latest published courses")
    link = "/cours/feed/"
    description = _(u"Latests courses published on www.france-universite-numerique-mooc.fr")
    __name__ = 'FUNRSS'

    def items(self, request):
        return courses.utils.sort_courses(get_courses(None))[:16]

    def item_title(self, course):
        return get_course_about_section(course, 'title')

    def item_description(self, course):
        course = courses.utils.dates_description(course)
        context = {}
        context['image_url'] = courses.utils.course_image_url(course) + '?width=300'
        context['short_description'] = get_course_about_section(course, 'short_description')
        context['course'] = course
        try:
            context['university'] = University.objects.get(code=course.org)
        except University.DoesNotExist:
            pass
        return render_to_string('course_pages/feed/feed.html', context)

    def item_link(self, course):
        return reverse('about_course', args=[course.id.to_deprecated_string()])
