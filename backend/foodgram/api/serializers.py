from django.db import IntegrityError
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField

from api.exceptions import SubscriptionError, IngredientRecipeCreateUpdateError, RecipeCreateUpdateError
from api.utils import (
    process_custom_context,
    process_recipe_ingredients_data,
)
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from users.models import Subscription, User


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class UserRecipeReadSerializer(serializers.ModelSerializer):
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
        try:
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
        except AttributeError:
            pass
        return process_custom_context(
            instance=obj,
            modelfield_first='subscribed_to',
            modelfield_second='subscriber',
            self=self,
            app_name='users',
            model_name='Subscription',
        )


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserRecipeReadSerializer(read_only=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source='RecipeIngredients'
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'image',
            'created',
            'cooking_time',
            'ingredients',
            'tags',
            'is_favorited',
            'is_in_shopping_cart',
        )
        depth = 1

    def get_is_favorited(self, obj):
        try:
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
        except AttributeError:
            pass
        return process_custom_context(
            instance=obj,
            modelfield_first='favorited_recipe',
            modelfield_second='favorited_user',
            self=self,
            app_name='recipes',
            model_name='Favorite',
        )

    def get_is_in_shopping_cart(self, obj):
        try:
            user = self.context.get('request').user
            if user.is_anonymous:
                return False
        except AttributeError:
            pass
        return process_custom_context(
            instance=obj,
            modelfield_first='shoppingcart_recipe',
            modelfield_second='shoppingcart_user',
            self=self,
            app_name='recipes',
            model_name='ShoppingCart',
        )


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = serializers.HiddenField(default=CurrentUserDefault())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'text',
            'image',
            'created',
            'cooking_time',
            'ingredients',
            'tags',
        )
        depth = 1

    def validate_tags(self, value):
        if not value:
            raise ValidationError({'tags': 'Отсутвует тег'})
        tags_list = []
        for tag in value:
            if tag in tags_list:
                raise ValidationError({'tags': 'Теги дублируются'})
            tags_list.append(tag)
        return value

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError({'ingredients': 'Выберите ингредиенты'})
        ingredients_list = []
        for item in value:
            if item in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингридиенты дублируются'}
                )
            if int(item['amount']) <= 0:
                raise ValidationError({'amount': 'Выберите число большее 0'})
            ingredients_list.append(item)
        return value

    def create(self, validated_data):
        try:
            tags = validated_data.pop('tags')
            recipe = Recipe.objects.create(**validated_data)
            process_recipe_ingredients_data(self, recipe)
            recipe.tags.set(tags)
            return recipe
        except IntegrityError as e:
            error_message = e.args[0]
            if 'unique_recipe_ingredients' in error_message:
                recipe.delete()
                raise IngredientRecipeCreateUpdateError()
            if 'unique_recipe' in error_message:
                recipe.delete()
                raise RecipeCreateUpdateError()

    def update(self, instance, validated_data):
        try:
            instance.ingredients.clear()
            process_recipe_ingredients_data(self, instance)
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
            return super().update(instance, validated_data)
        except IntegrityError as e:
            error_message = e.args[0]
            if 'unique_recipe_ingredients' in error_message:
                raise IngredientRecipeCreateUpdateError()
            if 'unique_recipe' in error_message:
                raise RecipeCreateUpdateError()


class FavoriteSerializer(serializers.ModelSerializer):
    favorited_user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = Favorite
        fields = (
            'id',
            'favorited_user',
            'favorited_recipe',
        )
        read_only_fields = fields
        depth = 1


class FavoriteDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = (
            'favorited_user',
            'favorited_recipe',
        )
        read_only_fields = fields
        depth = 1


class ShoppingCartSerializer(serializers.ModelSerializer):
    shoppingcart_user = serializers.HiddenField(default=CurrentUserDefault())

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'shoppingcart_user',
            'shoppingcart_recipe',
        )
        read_only_fields = fields
        depth = 1


class ShoppingCartDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = (
            'shoppingcart_user',
            'shoppingcart_recipe',
        )
        read_only_fields = fields
        depth = 1


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
        return process_custom_context(
            instance=obj,
            modelfield_first='subscribed_to',
            modelfield_second='subscriber',
            self=self,
            app_name='users',
            model_name='Subscription',
        )


class UserSubscriptionSerializer(UserReadSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserReadSerializer.Meta):
        fields = UserReadSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.id).count()

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj.id)
        recipes_limit = self.context.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        serializer = RecipeReadSerializer(
            recipes, many=True, read_only=True,
            context=self.context
        )
        return serializer.data


class MeReadSerializer(serializers.ModelSerializer):
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
        if Subscription.objects.filter(
            subscribed_to=obj, subscriber=obj
        ).exists():
            return True
        return False


class SubscriptionSerializer(serializers.ModelSerializer):
    subscriber = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    subscribed_to = serializers.PrimaryKeyRelatedField(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('subscribed_to')
        user_subscriber = data.pop('subscriber')
        context = {}
        context['user_subscriber'] = user_subscriber
        context['is_retrieve'] = True
        serializer = UserSubscriptionSerializer(
            instance.subscribed_to, context=context
        )
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

    def validate(self, data):
        subscribed_to = self.context.get('subscribed_to')
        subscriber = self.context.get('request').user
        if subscribed_to == subscriber:
            raise ValidationError(
                detail='Нельзя подписаться на свой аккаунт',
                code=status.HTTP_400_BAD_REQUEST,
            )
        if Subscription.objects.filter(
            subscribed_to=subscribed_to, subscriber=subscriber
        ).exists():
            raise ValidationError(
                detail='Вы уже подписаны на данного автора',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data


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
        user_subscriber = data.pop('subscriber')
        context = {}
        context['user_subscriber'] = user_subscriber
        context['is_list'] = True
        try:
            query_params_context = self.context.get('request').query_params
            recipes_limit = query_params_context.get('recipes_limit')
            context['recipes_limit'] = recipes_limit
        except AttributeError:
            pass
        serializer = UserSubscriptionSerializer(
            instance.subscribed_to, context=context
        )
        return serializer.data

    class Meta:
        model = Subscription
        fields = (
            'subscriber',
            'subscribed_to',
        )
        read_only_fields = fields
        depth = 1
