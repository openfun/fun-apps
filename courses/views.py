# -*- coding: utf-8 -*-

import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import Feed
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils import timezone, translation
from django.utils.translation import ugettext_lazy as _

from courseware.courses import get_courses, get_course_about_section

from universities.models import University

from .forms import CourseFilteringForm
from . import utils as courses_utils

COURSES_BY_PAGE = 24


def courses_index(request):
    courses = [courses_utils.dates_description(course) for course in get_courses(request.user)]
    form = CourseFilteringForm(request.GET or None)
    by = request.GET.get('by', COURSES_BY_PAGE)  # override default page size

    if form.is_valid():
        if form.cleaned_data['university']:
            university = University.objects.get(code=form.cleaned_data['university'])
            children = [child.code for child in university.children.all()]
            courses = [c for c in courses if c.org == form.cleaned_data['university'] or c.org in children]
        if form.cleaned_data['state']:
            now = timezone.make_aware(datetime.datetime.utcnow(), timezone.get_current_timezone())
            if form.cleaned_data['state'] == 'future':
                courses = [c for c in courses if c.start and c.start > now]
            elif form.cleaned_data['state'] == 'current':
                courses = [c for c in courses if c.start and c.start < now and c.end and c.end > now]
            elif form.cleaned_data['state'] == 'past':
                courses = [c for c in courses if c.end and c.end < now]
    elif form.errors:
        return redirect(courses_index)
    courses = courses_utils._sort_courses(courses)

    # paginate courses
    paginator = Paginator(courses, by, orphans=3)
    page = request.GET.get('page')

    try:
        courses = paginator.page(page)
    except PageNotAnInteger:
        courses = paginator.page(1)
    except EmptyPage:
        courses = paginator.page(paginator.num_pages)

    return render(request, 'courses/index.html', {
        'form': form,
        'courses': courses,
        'current_language': translation.get_language(),
    })



class CoursesFeed(Feed):
    title = _(u"Fun latest published courses")
    link = "/cours/feed/"
    description = _(u"Latests courses published on www.france-universite-numerique-mooc.fr")
    __name__ = 'FUNRSS'

    def items(self, request):
        return courses_utils._sort_courses(get_courses(None))[:16]

    def item_title(self, course):
        return get_course_about_section(course, 'title')

    def item_description(self, course):
        course = courses_utils.dates_description(course)
        context = {}
        context['image_url'] = course_image_url(course) + '?width=300'
        context['short_description'] = get_course_about_section(course, 'short_description')
        context['course'] = course
        try:
            context['university'] = University.objects.get(code=course.org)
        except University.DoesNotExist:
            pass
        return render_to_string('courses/feed/feed.html', context)

    def item_link(self, course):
        return reverse('about_course', args=[course.id.to_deprecated_string()])
