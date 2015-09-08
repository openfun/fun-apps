from rest_framework import serializers

from universities.serializers import UniversitySerializer
from .models import Course, CourseSubject


class CourseSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseSubject
        fields = ('id', 'name')


class CourseSerializer(serializers.ModelSerializer):
    universities = UniversitySerializer()
    subjects = CourseSubjectSerializer()
    image_url = serializers.CharField(source='image_url')
    short_description = serializers.CharField(source='short_description')
    title = serializers.CharField(source='title')

    class Meta:
        model = Course
        fields = (
            'id',
            'key',
            'title',
            'short_description',
            'universities',
            'level',
            'subjects',
            'image_url',
            'is_new',
            'on_demand',
            'start_date',
            'end_date',
            'score',
        )
