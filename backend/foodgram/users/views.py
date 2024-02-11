from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import User
from .serializers import UserReadSerializer, UserCreateSerializer


class UserViewSet(CreateModelMixin, ReadOnlyModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            serializer_class = UserReadSerializer
        else:
            serializer_class = UserCreateSerializer
        return serializer_class
