from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _


class FunAuthTokenSerializer(AuthTokenSerializer):

    def validate(self, attrs):
        super(FunAuthTokenSerializer, self).validate(attrs)
        user = attrs['user']
        if user.is_superuser:
            return attrs
        if not user.is_staff:
            msg = _('User is not staff member.')
            raise serializers.ValidationError(msg)
        return attrs
