
from rest_framework import serializers

from .models import University


class UniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = University
        fields = (
            'id',
            'name',
            'code',
            'logo',
            'detail_page_enabled',
            'banner',
        )
