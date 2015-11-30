from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers

from django.utils.translation import ugettext_lazy as _


class FunAuthTokenSerializer(AuthTokenSerializer):
    '''
    Adds specific authentication validation for FUN API.
    '''

    def validate(self, attrs):
        super(FunAuthTokenSerializer, self).validate(attrs)
        user = attrs['user']
        if user.is_staff or user.is_superuser:
            return attrs
        raise serializers.ValidationError(_('User is not staff member.'))
