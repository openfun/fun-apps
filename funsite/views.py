# -*- coding: utf-8 -*-

from django.shortcuts import render

from edxmako.shortcuts import render_to_response

from haystack.query import SearchQuerySet

from courses.models import Course
from newsfeed.models import Article

def render_static_template(request, page):
    return render(request, 'funsite/static_templates/%s.html' % page, {})


def search(request):
    results = []
    pattern = ''
    category_count = 0
    courses, articles = [], []
    if request.GET.get('q'):
        pattern = request.GET['q']
        results = SearchQuerySet().filter(content=pattern)

        if results:
            articles = Article.objects.filter(pk__in=[item.pk for item in results.filter(django_ct='newsfeed.article')])
            courses = Course.objects.filter(pk__in=[item.pk for item in results.filter(django_ct='courses.course')])
            category_count = sum([int(bool(category)) for category in [articles, courses]])

    result_count = len(results)
    return render_to_response('funsite/search-results.html', {
        'articles': articles,
        'courses': courses,
        'pattern': pattern,
        'category_count': category_count,
        'result_count': result_count,
        })

