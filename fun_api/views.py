from rest_framework.authtoken.views import ObtainAuthToken

from .serializers import FunAuthTokenSerializer


class GetToken(ObtainAuthToken):
    serializer_class = FunAuthTokenSerializer


get_token = GetToken.as_view()
