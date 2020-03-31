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
        "courses_count_starting_soon": Course.objects.starting_soon().count(),
        "courses_count_enrollment_ending_soon": Course.objects.enrollment_ends_soon().count(),
        "courses_count_new": Course.objects.new().count(),
        "courses_count_opened": Course.objects.opened().count(),
        "courses_count_started": Course.objects.started().count(),
        "courses_count_archived": Course.objects.archived().count(),
        "courses_count_browsable": Course.objects.browsable().count(),
    })


class FUNCustomFeedGenerator(Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super(FUNCustomFeedGenerator, self).add_item_elements(handler, item)
        handler.addQuickElement(u"university", item['university'])
        handler.addQuickElement(u"language", item['language'])
        handler.addQuickElement(u"level", item['level'])
        handler.addQuickElement(u"short_description", item['short_description'])
        handler.addQuickElement(u"thumbnail_url", item['thumbnail_url'])
        handler.addQuickElement(u"start_date", item['start_date'])
        handler.addQuickElement(u"end_date", item['end_date'])
        handler.addQuickElement(u"enrollment_start_date", item['enrollment_start_date'])
        handler.addQuickElement(u"enrollment_end_date", item['enrollment_end_date'])
        handler.addQuickElement(u"subjects", item['subjects'])


class CoursesFeed(Feed):
    title = _(u"Fun latest published courses")
    link = "/cours/feed/"
    description = _(u"Latests courses published on www.fun-mooc.fr")
    __name__ = 'FUNRSS'
    feed_type = FUNCustomFeedGenerator

    def get_site(self):
        protocol = 'https://'
        site = settings.SITE_NAME
        return protocol, site

    def items(self, request):
        return Course.objects.public()

    def item_title(self, course):
        return course.title

    def item_link(self, course):
        return course.get_absolute_url()

    # This will be rendered by aggregators
    def item_description(self, course):
        protocol, site = self.get_site()
        return render_to_string('course_pages/feed/feed.html', {
                'course': course,
                'protocol': protocol,
                'site': site,
                })

    def item_extra_kwargs(self, course):
        """
        Returns an extra keyword arguments dictionary that is used with
        the `add_item` call of the feed generator.
        Add the 'content' field of the 'Entry' item, to be used by the custom feed generator.
        """
        protocol, site = self.get_site()
        return {
            'university': course.university_name,
            'language': course.get_language_display(),
            'level': course.get_level_display(),
            'short_description': course.short_description,
            'subjects': ', '.join([s.name for s in course.subjects.all()]),
            'thumbnail_url': protocol + site + course.get_thumbnail_url('big'),
            'start_date': course.start_date.isoformat() if course.start_date else '',
            'end_date': course.end_date.isoformat() if course.end_date else '',
            'enrollment_start_date': course.enrollment_start_date.isoformat() if course.enrollment_start_date else '',
            'enrollment_end_date': course.enrollment_end_date.isoformat() if course.enrollment_end_date else '',
        }
