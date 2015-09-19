from rest_framework import filters


class CourseFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        university_codes = request.QUERY_PARAMS.getlist('university')
        subject_slugs = request.QUERY_PARAMS.getlist('subject')
        levels = request.QUERY_PARAMS.getlist('level')
        availability = request.QUERY_PARAMS.getlist('availability')
        if university_codes:
            queryset = queryset.filter(universities__code__in=university_codes)
        if subject_slugs:
            queryset = queryset.filter(subjects__slug__in=subject_slugs)
        if levels:
            queryset = queryset.filter(level__in=levels)
        if 'new' in availability:
            queryset = queryset.new()
        if 'on-demand' in availability:
            queryset = queryset.on_demand()
        if 'start-soon' in availability :
            queryset = queryset.start_soon()
        if 'end-soon' in availability:
            queryset = queryset.end_soon()
        return queryset
