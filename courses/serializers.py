from rest_framework import serializers

from universities.serializers import UniversitySerializer
from .models import Course, CourseSubject


class CourseSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseSubject
        fields = ('id', 'name')


class CourseSerializer(serializers.ModelSerializer):
    university = UniversitySerializer()
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
            'university',
            'level',
            'subjects',
            'image_url',
        )
