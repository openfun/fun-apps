
from rest_framework import serializers

from fun_api import serializers as fun_serializers
from universities.models import University


class UniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = University
        fields = (
            'id', 'name', 'code', 'logo', 'banner')


class UniversityStaffSerializer(fun_serializers.UpdateSerializerMixin, UniversitySerializer):
    """
    Presents data accessible to authenticated staff users.
    """

    class Meta(UniversitySerializer.Meta):
        fields = UniversitySerializer.Meta.fields + (
            'score', 'partnership_level', 'prevent_auto_update')
        # All fields are readonly except "score"
        read_only_fields = UniversitySerializer.Meta.fields + (
            'partnership_level', 'prevent_auto_update')
