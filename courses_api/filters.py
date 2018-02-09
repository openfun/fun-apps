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
        status = request.query_params.getlist('status')
        full_text_query = request.query_params.get('query', None)

        if university_codes:
            queryset = queryset.filter(universities__code__in=university_codes)
        if subject_slugs:
            queryset = queryset.filter(subjects__slug__in=subject_slugs)
        if levels:
            queryset = queryset.filter(level__in=levels)
        if languages:
            queryset = queryset.filter(language__in=languages)
        # Status
        if 'new' in status:
            queryset = queryset.new()
        # Availability
        if 'starting_soon' in availability:
            queryset = queryset.starting_soon()
        elif 'enrollment_ending_soon' in availability:
            queryset = queryset.enrollment_ends_soon()
        elif 'opened' in availability:
            queryset = queryset.opened()
        elif 'started' in availability:
            queryset = queryset.started()
        elif 'archived' in availability:
            queryset = queryset.archived()

        if full_text_query:
            results = SearchQuerySet().filter(content=full_text_query)
            queryset = queryset.filter(
                pk__in=[item.pk for item in results.filter(django_ct='courses.course')])

        # A sorting that makes sense depends on which filter is applied
        queryset = queryset.annotate_for_ordering()
        if 'archived' in availability:
            order_param = '-end_date'
        else:
            order_param = 'ordering_date'

        queryset = queryset.order_by('has_ended', 'is_enrollment_over', '-has_started', order_param)

        return queryset
