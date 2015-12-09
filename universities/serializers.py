from rest_framework import serializers

from .models import University


# TODO this module is not used in the CMS. In fact, no university view or url
# should not be installed in the CMS. So we should move these modules to a
# separate universities_api app.
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

    class Meta(UniversitySerializer.Meta):
        fields = UniversitySerializer.Meta.fields + ('score',)
