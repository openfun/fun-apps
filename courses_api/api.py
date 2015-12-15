from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from courses.models import Course

from .filters import CourseFilter
from .serializers import (
    CourseSerializer, PrivateCourseSerializer, CourseScoreSerializer,
)


def is_true(value):
    return str(value).lower() in ['true', '1', 'y', 'yes']


class CourseAPIView(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    '''
    ## Filtering

    The API allows for filtering the list of courses.

    * By universities: `university=CNAM&university=CentraleParis`
    * By course subjects: `subject=philosophy&subject=science`
    * By availability:
        * `availability=start-soon`
        * `availability=end-soon`
        * `availability=enrollment-ends-soon`
        * `availability=new`

    ## Pagination

    You can limit the number of Results Per Page using the `rpp`
    API parameter.

    * Pagination: `/api/courses/locations/?rpp=6`

    By default, pagination is set to 10.

    ## Extended List of Courses

    Only courses that are shown in the courses catalog are listed in the
    public API. Admin API users can access an extended list of courses -
    courses that are not shown in catalog. When logged in as admin,
    you can use the `extended_list` parameter.

    * Extended list: `/api/courses/?extended_list=True`

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
    def extended_list(self):
        extended_list = self.request.QUERY_PARAMS.get('extended_list')
        return is_true(extended_list)

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.is_admin:
            if self.action == 'update':
                return CourseScoreSerializer
            if self.action in ('retrieve', 'list'):
                return PrivateCourseSerializer
        if self.action in ('retrieve', 'list'):
            return CourseSerializer

    def get_queryset(self):
        queryset = super(CourseAPIView, self).get_queryset()
        queryset = queryset.filter(is_active=True)  # Not active means deleted.
        if self.is_admin and self.extended_list:
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
