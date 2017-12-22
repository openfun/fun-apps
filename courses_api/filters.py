# -*- coding: utf-8 -*-

from rest_framework import filters

from haystack.query import SearchQuerySet


class CourseFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        university_codes = request.query_params.getlist('university')
        subject_slugs = request.query_params.getlist('subject')
        levels = request.query_params.getlist('level')
        languages = request.query_params.getlist('language')
        availability = request.query_params.getlist('availability')
        full_text_query = request.query_params.get('query', None)

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

        # A sorting that makes sense depends on which filter is applied
        if {'end-soon', 'enrollment-ends-soon', 'opened', 'archived'}.intersection(set(availability)):
            queryset = queryset.order_by('end_date')
        else:
            queryset = queryset.order_by('start_date')

        return queryset
