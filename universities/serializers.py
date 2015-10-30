from rest_framework import serializers

from courses.serializers_utils import CoursesCountSerializerMixin

from .models import University


class UniversitySerializer(serializers.ModelSerializer, CoursesCountSerializerMixin):
    courses_count = serializers.SerializerMethodField(method_name='get_courses_count')

    class Meta:
        model = University
        fields = (
            'id',
            'name',
            'code',
            'logo',
            'detail_page_enabled',
            'banner',
            'courses_count',
        )
