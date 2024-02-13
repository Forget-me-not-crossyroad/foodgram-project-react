from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from .models import User, Me, SetPassword, Subscription
from .serializers import UserReadSerializer, UserCreateSerializer, MeReadSerializer, SetPasswordSerializer, \
    SubscriptionSerializer


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


class MeViewSet(ListModelMixin, GenericViewSet):
    queryset = Me.objects.all()
    serializer_class = MeReadSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None

    def get_queryset(self):
        user_id = self.request.user.id
        return Me.objects.filter(id=user_id)

    def list(self, request, *args, **kwargs):
        serializer = MeReadSerializer(self.get_queryset(), many=True)
        return Response(serializer.data[0])


class SetPasswordViewSet(CreateModelMixin, GenericViewSet):
    queryset = SetPassword.objects.all()
    serializer_class = SetPasswordSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None


class SubscriptionViewSet(CreateModelMixin, GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None

    def get_queryset(self):
        return self.request.user.subscriber.all()

    def perform_create(self, serializer):
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
        serializer.save(subscriber=self.request.user, subscribed_to=subscribed_to)
