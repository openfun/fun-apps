
from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAdminUser, AllowAny

from .models import University
from .serializers import UniversitySerializer, UniversityStaffSerializer


class UniversityAPIViewSet(
        mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
        viewsets.GenericViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    paginate_by = 100
    paginate_by_param = 'rpp'
    max_paginate_by = None

    def get_permissions(self):
        """
        Anybody, including anonymous users can read.
        Only staff users can update.
        """
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        """
        The serializer class differs to enable the following behaviors:
        - Staff users are allowed to see more fields,
        - Update is only allowed for staff users and only on the score field,
        - Other users can only read with less fields (list or detail).
        """
        if self.request.user.is_staff:
                return UniversityStaffSerializer
        return UniversitySerializer

    def get_queryset(self):
        return University.objects.all()
