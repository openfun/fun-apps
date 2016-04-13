# -*- coding: utf-8 -*-

from django.db import connection
from django.utils.timezone import now

from rest_framework import filters

from haystack.query import SearchQuerySet


class CourseFilter(filters.BaseFilterBackend):

    def order_by_param(self, request):
        """Get the "sort" parameter from the request

        Returns:
            str: value that can be fed to a .order_by() directive.
        """
        sort_param = request.QUERY_PARAMS.get("sort")
        allowed_sort_params = ('enrollment_start_date', 'score', 'start_date', 'title',)
        for allowed_param in allowed_sort_params:
            if sort_param == allowed_param or sort_param == '-' + allowed_param:
                return sort_param
        return '-score'

    def filter_queryset(self, request, queryset, view):
        university_codes = request.QUERY_PARAMS.getlist('university')
        subject_slugs = request.QUERY_PARAMS.getlist('subject')
        levels = request.QUERY_PARAMS.getlist('level')
        languages = request.QUERY_PARAMS.getlist('language')
        availability = request.QUERY_PARAMS.getlist('availability')
        full_text_query = request.QUERY_PARAMS.get('query', None)

        if university_codes:
            queryset = queryset.filter(universities__code__in=university_codes)
        if subject_slugs:
            queryset = queryset.filter(subjects__slug__in=subject_slugs)
        if levels:
            queryset = queryset.filter(level__in=levels)
        if languages:
            queryset = queryset.filter(language__in=languages)
        if 'start-soon' in availability:
            queryset = queryset.start_soon()
        if 'end-soon' in availability:
            queryset = queryset.end_soon()
        if 'enrollment-ends-soon' in availability:
            queryset = queryset.enrollment_ends_soon()
        if 'new' in availability:
            queryset = queryset.new()
        if 'current' in availability:
            queryset = queryset.current()
        if full_text_query:
            results = SearchQuerySet().filter(content=full_text_query)
            queryset = queryset.filter(pk__in=[item.pk for item in results.filter(django_ct='courses.course')])

        # Put archived courses at the end
        # Note: we are putting raw sql in the extra(...) statement. To do that,
        # we need the proper datetime formatting, which varies for every db.
        formatted_now = connection.ops.value_to_db_datetime(now())
        queryset = queryset.extra(select={
            'is_archived': 'end_date < "{now}" OR enrollment_end_date < "{now}"'.format(now=formatted_now)
        })

        queryset = queryset.order_by('is_archived', self.order_by_param(request))

        return queryset
