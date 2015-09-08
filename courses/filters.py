from django.utils.timezone import now, timedelta

from rest_framework import filters


def is_true(value):
    return value.lower() in ('true', 'yes', '1', 'y')


class CourseFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        university_codes = request.QUERY_PARAMS.getlist('university')
        subject_slugs = request.QUERY_PARAMS.getlist('subject')
        levels = request.QUERY_PARAMS.getlist('level')
        new_only = request.QUERY_PARAMS.get('new_only', 'false')
        on_demand_only = request.QUERY_PARAMS.get('on_demand_only', 'false')
        start_soon_only = request.QUERY_PARAMS.get('start_soon_only', 'false')
        end_soon_only = request.QUERY_PARAMS.get('end_soon_only', 'false')
        if university_codes:
            queryset = queryset.filter(universities__code__in=university_codes)
        if subject_slugs:
            queryset = queryset.filter(subjects__slug__in=subject_slugs)
        if levels:
            queryset = queryset.filter(level__in=levels)
        if is_true(new_only):
            queryset = queryset.filter(is_new=True)
        if is_true(on_demand_only):
            queryset = queryset.filter(on_demand=True)
        too_late = now() + timedelta(days=7)  # TODO: Move in settings.
        if is_true(start_soon_only):
            queryset = queryset.filter(start_date__range=(now(), too_late))
        if is_true(end_soon_only):
            queryset = queryset.filter(end_date__range=(now(), too_late))
        return queryset
