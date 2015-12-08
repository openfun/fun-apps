from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from courses.models import Course

from .filters import CourseFilter
from .serializers import (
    PublicCourseSerializer, PrivateCourseSerializer, CourseScoreSerializer,
)


def is_true(value):
    return str(value).lower() in ['true', '1', 'y', 'yes']


class CourseAPIView(viewsets.ReadOnlyModelViewSet):
    '''
    ## Filtering

    The API allows for filtering the list of courses.

    * By universities: /api/?university=CNAM&university=CentraleParis
    * By course subjects: /api/?subject=philosophy&subject=science
    * By course level: /api/?level=advanced
    * By availability: 'start-soon', 'end-soon'
        * /api/?availability=start-soon

    ## Pagination

    You can limit the number of Results Per Page using the rpp API parameter.

    /api/locations/?rpp=6

    By default, pagination is set to 10.

    '''
    filter_backends = (CourseFilter,)
    model = Course
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    paginate_by = 100
    paginate_by_param = 'rpp'
    max_paginate_by = None

    @property
    def is_admin(self):
        is_admin = self.request.user.is_staff or self.request.user.is_superuser
        return is_admin

    @property
    def catalog_only(self):
        catalog_only = self.request.QUERY_PARAMS.get('catalog_only')
        return is_true(catalog_only)

    def get_serialiser_class(self):
        if self.is_admin:
            return PrivateCourseSerializer
        return PublicCourseSerializer

    def get_queryset(self):
        queryset = super(CourseAPIView, self).get_queryset()
        queryset = queryset.filter(is_active=True)  # Not active means deleted.
        if self.is_admin and self.catalog_only:
            queryset = queryset.with_related()
        else:
            queryset = queryset.with_related().public()
        queryset = self.filter_queryset(queryset)
        return queryset


class CourseScoreView(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Course.objects.all()
    serializer_class = CourseScoreSerializer
