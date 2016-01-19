from rest_framework import serializers

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
        fields = UniversitySerializer.Meta.fields + (
            'score',
            'partnership_level',
        )


class UniversityUpdateSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(required=False)

    class Meta:
        model = University
        fields = ('score',)
