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

    class Meta:
        model = Course
        fields = (
            'id',
            'key',
            'university',
            'level',
            'subjects',
            'image_url',
        )
