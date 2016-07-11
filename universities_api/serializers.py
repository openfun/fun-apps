from rest_framework import serializers

from fun_api import serializers as fun_serializers
from universities.models import University


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


class PrivateUniversitySerializer(UniversitySerializer):
    '''
    Presents data accessible to authenticated admin users.
    '''

    class Meta(UniversitySerializer.Meta):
        fields = (
            'id',
            'name',
            'code',
            'logo',
            'detail_page_enabled',
            'banner',
            'score',
            'partnership_level',
            'prevent_auto_update',
        )


class UniversityUpdateSerializer(fun_serializers.UpdateSerializerMixin, serializers.ModelSerializer):
    score = serializers.IntegerField(required=False)

    class Meta:
        model = University
        fields = ('score',)
