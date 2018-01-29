
from django.core.exceptions import PermissionDenied

from rest_framework.authtoken.serializers import AuthTokenSerializer


class FunAuthTokenSerializer(AuthTokenSerializer):
    """
    Adds specific authentication validation for FUN API.
    """

    def validate(self, attrs):
        super(FunAuthTokenSerializer, self).validate(attrs)
        user = attrs['user']
        if user.is_staff or user.is_superuser:
            return attrs
        raise PermissionDenied()


class UpdateSerializerMixin(object):
    """
    Helpers and common functionalities for update serializers,
    for instance for Course and University validation on update.
    """

    def validate(self, data):
        if self.instance.prevent_auto_update:
            raise PermissionDenied()
        return data
