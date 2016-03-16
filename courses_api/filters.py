# -*- coding: utf-8 -*-


from rest_framework import filters

from haystack.query import SearchQuerySet


class CourseFilter(filters.BaseFilterBackend):

    def order_by(self, request):
        """Get the "sort" parameter from the request

        Returns:
            tuple: value that can be fed to a .order_by() directive.
        """
        sort_param = request.QUERY_PARAMS.get("sort")
        if sort_param == "title":
            return ("title",)
        elif sort_param == "enrollment_start_date":
            return ("enrollment_start_date",)
        elif sort_param == "-enrollment_start_date":
            return ("-enrollment_start_date",)
        elif sort_param == "start_date":
            return ("start_date",)
        elif sort_param == "-start_date":
            return ("-start_date",)
        return ("-score",)

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
        if full_text_query:
            results = SearchQuerySet().filter(content=full_text_query)
            queryset = queryset.filter(pk__in=[item.pk for item in results.filter(django_ct='courses.course')])
        queryset = queryset.order_by(*self.order_by(request))
        return queryset
