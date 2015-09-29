from rest_framework import viewsets

from .serializers import CourseSerializer
from .models import Course
from .filters import CourseFilter


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
    authentication_classes = ()  # Disable auth - works with nginx.
    paginate_by = 10
    paginate_by_param = 'rpp'
    serializer_class = CourseSerializer

    def get_queryset(self):
        queryset = super(CourseAPIView, self).get_queryset()
        queryset = queryset.with_related().active()
        queryset = self.filter_queryset(queryset)
        return queryset
