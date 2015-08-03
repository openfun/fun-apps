from rest_framework import serializers

from universities.serializers import UniversitySerializer
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    university = UniversitySerializer()

    class Meta:
        model = Course
        fields = (
            'id',
            'key',
            'university',
            'level',
            'subjects',
        )
