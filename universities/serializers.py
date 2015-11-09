from rest_framework import serializers

from courses_api.serializers_utils import CoursesCountSerializerMixin

from .models import University


# TODO this module is not used in the CMS. In fact, no university view or url
# should not be installed in the CMS. So we should move these modules to a
# separate universities_api app.
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
