from rest_framework import viewsets
from rest_framework.response import Response

from universities.models import University
from universities.serializers import UniversitySerializer

from .serializers import CourseSerializer, CourseSubjectSerializer
from .models import Course, CourseSubject


class CourseAPIView(viewsets.ViewSet):
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

    '''

    def get_courses_queryset(self):
        queryset = Course.objects.prefetch_related('subjects', 'universities')
        university_codes = self.request.QUERY_PARAMS.getlist('university')
        subject_slugs = self.request.QUERY_PARAMS.getlist('subject')
        levels = self.request.QUERY_PARAMS.getlist('level')
        if university_codes:
            queryset = queryset.filter(universities__code__in=university_codes)
        if subject_slugs:
            queryset = queryset.filter(subjects__slug__in=subject_slugs)
        if levels:
            queryset = queryset.filter(level__in=levels)
        return queryset

    def get_serialized_courses(self):
        queryset = self.get_courses_queryset()
        serializer = CourseSerializer(queryset, many=True)
        return serializer.data

    def get_serialized_universities(self, course_id_list=None):
        queryset = University.objects.all()
        if course_id_list:
            queryset = queryset.filter(courses__id__in=course_id_list).distinct()
        serializer = UniversitySerializer(queryset)
        return serializer.data

    def get_serialized_course_subjects(self, course_id_list=None):
        queryset = CourseSubject.objects.all()
        if course_id_list:
            queryset = queryset.filter(courses__id__in=course_id_list).distinct()
        serializer = CourseSubjectSerializer(queryset)
        return serializer.data

    def list(self, request, *args, **kwargs):
        courses_data = self.get_serialized_courses()
        courses_id_list = self.get_courses_queryset().values_list('id', flat=True)
        universities_data = self.get_serialized_universities(courses_id_list)
        course_subjects_data = self.get_serialized_course_subjects(courses_id_list)
        data = {
            'courses': courses_data,
            'universities': universities_data,
            'course_subjects': course_subjects_data,
        }
        return Response(data)
