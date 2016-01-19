from rest_framework import viewsets, mixins
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny

from universities.models import University

from .serializers import (UniversitySerializer, PrivateUniversitySerializer,
    UniversityUpdateSerializer)


class UniversityAPIView(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    viewsets.GenericViewSet):
    model = University
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    paginate_by = 100
    paginate_by_param = 'rpp'
    max_paginate_by = None

    @property
    def is_admin(self):
        is_admin = self.request.user.is_staff or self.request.user.is_superuser
        return is_admin

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.is_admin:
            if self.action == 'update':
                return UniversityUpdateSerializer
            if self.action in ('retrieve', 'list'):
                return PrivateUniversitySerializer
        if self.action in ('retrieve', 'list'):
            return UniversitySerializer
