from rest_framework import viewsets
from rest_framework.filters import DjangoFilterBackend

from .models import Course


class CourseAPIView(viewsets.ReadOnlyModelViewSet):
    paginate_by = 10
    paginate_by_param = 'rpp'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('university', 'subjects', 'level')
    model = Course
