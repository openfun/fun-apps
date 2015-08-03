from rest_framework import viewsets
from rest_framework.filters import DjangoFilterBackend

from .serializers import CourseSerializer
from .models import Course


class CourseAPIView(viewsets.ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    paginate_by = 10
    paginate_by_param = 'rpp'
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('university', 'subjects', 'level')

    def get_queryset(self):
        queryset = Course.objects.prefetch_related('subjects', 'university')
        return queryset
