from api.serializers import RecipeReadSerializer
from django.core.exceptions import BadRequest
from django.db import IntegrityError
from django.http import Http404
from django.utils import timezone
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault

from .exceptions import SubscriptionError
from .models import Me, SetPassword, Subscription, User


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'}
    )
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
        if Subscription.objects.filter(subscribed_to=obj).exists():
            return True
        return False


class UserSubscriptionSerializer(UserReadSerializer):
    recipes = RecipeReadSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        if Recipe.objects.filter(author=obj.id).exists():
            return Recipe.objects.filter(author=obj.id).count()
        return 0


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
        if Subscription.objects.filter(subscribed_to=obj).exists():
            return True
        return False


class SetPasswordSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=CurrentUserDefault())
    created = serializers.HiddenField(default=timezone.now)
    current_password = serializers.CharField(
        write_only=True, style={'input_type': 'current_password'}
    )
    new_password = serializers.CharField(
        write_only=True, style={'input_type': 'new_password'}
    )

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except BadRequest as e:
            raise Http404(e)

    class Meta:
        model = SetPassword
        fields = (
            'user',
            'created',
            'current_password',
            'new_password',
        )
        read_only_fields = fields
        depth = 1


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    subscribed_to = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('subscribed_to')
        data.pop('subscriber')
        serializer = UserSubscriptionSerializer(instance.subscriber)
        return serializer.data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise SubscriptionError()

    class Meta:
        model = Subscription
        fields = (
            'subscriber',
            'subscribed_to',
        )
        read_only_fields = fields
        depth = 1


class SubscriptionDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = (
            'subscriber',
            'subscribed_to',
        )
        read_only_fields = fields
        depth = 1


class SubscriptionsSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('subscribed_to')
        data.pop('subscriber')
        serializer = UserSubscriptionSerializer(instance.subscribed_to)
        return serializer.data

    class Meta:
        model = Subscription
        fields = (
            'subscriber',
            'subscribed_to',
        )
        read_only_fields = fields
        depth = 1
