from django.db.models import Count

from rest_framework import viewsets
from rest_framework.filters import DjangoFilterBackend
from rest_framework.response import Response

from universities.models import University
from universities.serializers import UniversitySerializer

from .serializers import CourseSerializer, CourseSubjectSerializer
from .models import Course, CourseSubject
from .filters import CourseFilter


class CourseAPIView(viewsets.ReadOnlyModelViewSet):
    '''
    Returns list of courses.

    ## API Response
    The API response is a document structured like this:

    ```
    {
        "courses": [ ],
        "universities": [ ],
        "course_subjects": [ ]
    }
    ```

    The response contains, not only the list of courses, but also the list
    of items used for filters usually displayed on sidebar - universities,
    course subjects, etc.

    ## Filtering

    The API allows for filtering the list of courses.

    * By universities: /api/?university=CNAM&university=CentraleParis
    * By course subjects: /api/?subject=philosophy&subject=science
    * By course level: /api/?level=advanced
    * By availability: 'new', 'on-demand', 'start-soon', 'end-soon'
        * /api/?availability=new

    '''
    filter_backends = (CourseFilter,)
    model = Course

    def get_queryset(self):
        queryset = super(CourseAPIView, self).get_queryset()
        queryset = queryset.prefetch_related('subjects', 'universities')
        queryset = self.filter_queryset(queryset)
        return queryset

    def get_serialized_courses(self):
        queryset = self.get_queryset()
        serializer = CourseSerializer(queryset, many=True)
        return serializer.data

    def get_serialized_universities(self, course_id_list):
        queryset = University.objects.with_related()
        queryset = queryset.filter(courses__id__in=course_id_list)
        serializer = UniversitySerializer(queryset)
        return serializer.data

    def get_serialized_course_subjects(self, course_id_list):
        queryset = CourseSubject.objects.with_related()
        queryset = queryset.filter(courses__id__in=course_id_list)
        queryset = queryset.annotate(courses_count=Count('courses'))
        serializer = CourseSubjectSerializer(queryset)
        return serializer.data

    def list(self, request, *args, **kwargs):
        courses_data = self.get_serialized_courses()
        courses_id_list = self.get_queryset().values_list('id', flat=True)
        universities_data = self.get_serialized_universities(courses_id_list)
        course_subjects_data = self.get_serialized_course_subjects(courses_id_list)
        data = {
            'courses': courses_data,
            'universities': universities_data,
            'course_subjects': course_subjects_data,
        }
        return Response(data)
