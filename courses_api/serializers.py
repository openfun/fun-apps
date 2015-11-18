# -*- coding: utf-8 -*-

from rest_framework import serializers

from courses.models import Course, CourseSubject
from universities.models import University
from universities.serializers import UniversitySerializer

from .serializers_utils import CoursesCountSerializerMixin


class CourseSubjectSerializer(CoursesCountSerializerMixin, serializers.ModelSerializer):
    courses_count = serializers.SerializerMethodField(method_name='get_courses_count')

    class Meta:
        model = CourseSubject
        fields = ('id', 'name', 'courses_count')


class CourseSerializer(serializers.ModelSerializer):
    universities = serializers.SerializerMethodField('get_universities')
    subjects = CourseSubjectSerializer()
    session_display = serializers.CharField(source='session_display')
    thumbnails = serializers.CharField(source='thumbnails_info')
    start_date_display = serializers.CharField(source='start_date_display')
    enrollment_ended = serializers.BooleanField(source='enrollment_ended')

    def get_universities(self, course):
        queryset = University.objects.active_by_score()
        serializer = UniversitySerializer(instance=queryset, many=True)
        return serializer.data

    class Meta:
        model = Course
        fields = (
            'id',
            'key',
            'universities',
            'title',
            'short_description',
            'level',
            'subjects',
            'image_url',
            'start_date',
            'start_date_display',
            'end_date',
            'enrollment_ended',
            'session_number',
            'session_display',
            'thumbnails',
        )
