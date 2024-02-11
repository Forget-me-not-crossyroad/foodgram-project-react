import django.core.exceptions
from rest_framework import serializers, status
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import User, Me


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    date_joined = serializers.HiddenField(default=timezone.now)
    is_active = serializers.HiddenField(default=True)
    is_staff = serializers.HiddenField(default=False)
    is_superuser = serializers.HiddenField(default=False)

    def create(self, validated_data):
        try:
            return User.objects.create_user(**validated_data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'password',
            'email',
            'id',
            'username',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
        )


class UserReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
            'id',
            'username',
            'is_subscribed',
        )
        read_only_fields = fields
        depth = 1

    def get_is_subscribed(self, obj):
        return False


class MeReadSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Me
        fields = (
            'first_name',
            'last_name',
            'email',
            'id',
            'username',
            'is_subscribed',
        )
        read_only_fields = fields
        depth = 1

    def get_is_subscribed(self, obj):
        return False

