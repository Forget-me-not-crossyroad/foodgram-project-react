from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet

from .models import User, Me, SetPassword, Subscription
from .serializers import UserReadSerializer, UserCreateSerializer, MeReadSerializer, SetPasswordSerializer, \
    SubscriptionSerializer, SubscriptionsSerializer, SubscriptionDeleteSerializer


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

    def retrieve(self, request, *args, **kwargs):
        if not User.objects.filter(id=self.kwargs.get('pk')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        super().retrieve(request, *args, **kwargs)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    def create(self, request, *args, **kwargs):
        try:
            super().create(request, *args, **kwargs)
            return Response({'success': 'Пароль успешно изменен.'}, status=status.HTTP_204_NO_CONTENT)
        except Http404:
            return Response({'errors': 'Введен неверный существующий пароль.'}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None

    def get_queryset(self):
        return self.request.user.subscriber.all()

    def get_serializer_class(self):
        if self.action in ('delete',):
            serializer_class = SubscriptionDeleteSerializer
        else:
            serializer_class = SubscriptionSerializer
        return serializer_class

    def perform_create(self, serializer):
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
        serializer.save(subscriber=self.request.user, subscribed_to=subscribed_to)

    def delete(self, request, *args, **kwargs):
        if not Subscription.objects.filter(subscribed_to=self.kwargs.get('user_id')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
        subscription = get_object_or_404(Subscription, subscriber=self.request.user, subscribed_to=subscribed_to)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        if not User.objects.filter(id=self.kwargs.get('user_id')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return super().create(request, *args, **kwargs)


class SubscriptionsViewSet(ReadOnlyModelViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionsSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    # pagination_class = None

    def get_queryset(self):
        subscriber = self.request.user
        return Subscription.objects.filter(subscriber=subscriber)
