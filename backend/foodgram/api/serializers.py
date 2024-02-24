from django.core.exceptions import BadRequest
from django.db import IntegrityError
from django.http import Http404
from django.utils import timezone
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError

from api.exceptions import SubscriptionError
from recipes.models import (Favorite, Ingredient, IngredientAmountRecipe,
                            IngredientRecipe, Recipe, ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField
from users.models import Subscription, User, SetPassword, Me


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


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmountRecipe
        fields = (
            'id',
            'amount',
        )


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(source='amount.amount')

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
        if Subscription.objects.filter(subscribed_to=obj).exists():
            return True
        return False


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    author = UserRecipeReadSerializer(read_only=True)

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientRecipeSerializer(
            IngredientRecipe.objects.filter(recipe=instance), many=True
        ).data
        return ingredients

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
        if Favorite.objects.filter(favorited_recipe=obj).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if ShoppingCart.objects.filter(shoppingcart_recipe=obj).exists():
            return True
        return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = serializers.HiddenField(default=CurrentUserDefault())
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
        if Favorite.objects.filter(favorited_recipe=obj).exists():
            return True
        return False

    def get_is_in_shopping_cart(self, obj):
        if ShoppingCart.objects.filter(shoppingcart_recipe=obj).exists():
            return True
        return False

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            recipe = Recipe.objects.create(**validated_data)
            return recipe
        tags = validated_data.pop('tags')
        context = self.context['request']
        ingredients = context.data['ingredients']
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            ingredient_for_recipe_id = ingredient['id']
            amount_for_recipe = ingredient['amount']
            ingredient_for_recipe = Ingredient.objects.get(
                id=ingredient_for_recipe_id
            )
            ingredient_amount_recipe = IngredientAmountRecipe.objects.create(
                amount=amount_for_recipe
            )
            IngredientRecipe.objects.create(
                recipe=recipe,
                amount=ingredient_amount_recipe,
                ingredient=ingredient_for_recipe,
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if not self.context['request'].data['ingredients'] is None:
            context = self.context['request']
            ingredients = context.data['ingredients']
            instance.ingredients.clear()
            for ingredient in ingredients:
                ingredient_for_recipe_id = ingredient['id']
                amount_for_recipe = ingredient['amount']
                ingredient_for_recipe = Ingredient.objects.get(
                    id=ingredient_for_recipe_id
                )
                ingredient_amount_recipe = (
                    IngredientAmountRecipe.objects.create(
                        amount=amount_for_recipe
                    )
                )
                IngredientRecipe.objects.create(
                    recipe=instance,
                    amount=ingredient_amount_recipe,
                    ingredient=ingredient_for_recipe,
                )
        if not validated_data.get('tags') is None:
            instance.tags.clear()
            tags = validated_data.pop('tags')
            instance.tags.set(tags)
        return super().update(instance, validated_data)


class FavoriteSerializer(serializers.ModelSerializer):
    favorited_user = serializers.HiddenField(default=CurrentUserDefault())
    name = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('favorited_recipe')
        return data

    class Meta:
        model = Favorite
        fields = (
            'id',
            'favorited_user',
            'favorited_recipe',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = fields
        depth = 1

    def get_name(self, obj):
        if Recipe.objects.get(id=obj.favorited_recipe.id):
            return Recipe.objects.get(id=obj.favorited_recipe.id).name
        return None

    def get_cooking_time(self, obj):
        if Recipe.objects.get(id=obj.favorited_recipe.id):
            return Recipe.objects.get(id=obj.favorited_recipe.id).cooking_time
        return None

    def get_image(self, obj):
        request = self.context.get('request')
        if Recipe.objects.get(id=obj.favorited_recipe.id):
            photo_url = Recipe.objects.get(
                id=obj.favorited_recipe.id
            ).image.url
            return request.build_absolute_uri(photo_url)
        return None


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
    name = serializers.SerializerMethodField()
    cooking_time = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('shoppingcart_recipe')
        return data

    class Meta:
        model = ShoppingCart
        fields = (
            'id',
            'shoppingcart_user',
            'shoppingcart_recipe',
            'name',
            'image',
            'cooking_time',
        )
        read_only_fields = fields
        depth = 1

    def get_name(self, obj):
        if Recipe.objects.get(id=obj.shoppingcart_recipe.id):
            return Recipe.objects.get(id=obj.shoppingcart_recipe.id).name
        return None

    def get_cooking_time(self, obj):
        if Recipe.objects.get(id=obj.shoppingcart_recipe.id):
            return Recipe.objects.get(
                id=obj.shoppingcart_recipe.id
            ).cooking_time
        return None

    def get_image(self, obj):
        request = self.context.get('request')
        if Recipe.objects.get(id=obj.shoppingcart_recipe.id):
            photo_url = Recipe.objects.get(
                id=obj.shoppingcart_recipe.id
            ).image.url
            return request.build_absolute_uri(photo_url)
        return None


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
        context = self.context
        if not context.get('is_list') is None:
            user = context['user_subscriber']['username']
            subscriber_user = User.objects.filter(username=user).get()
            if Subscription.objects.filter(subscribed_to=subscriber_user, subscriber=subscriber_user).exists():
                return True
        if not context.get('is_retrieve') is None:
            user = context['user_subscriber']
            subscriber_user = User.objects.filter(username=user).get()
            if Subscription.objects.filter(subscribed_to=obj, subscriber=subscriber_user).exists():
                return True
        if Subscription.objects.filter(subscribed_to=subscriber_user, subscriber=obj).exists():
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
        if Subscription.objects.filter(subscribed_to=obj, subscriber=obj).exists():
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
        user_subscriber = data.pop('subscriber')
        context = {}
        context['user_subscriber'] = user_subscriber
        context['is_retrieve'] = True
        serializer = UserSubscriptionSerializer(instance.subscribed_to,  context=context)
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
        user_subscriber = data.pop('subscriber')
        context = {}
        context['user_subscriber'] = user_subscriber
        context['is_list'] = True
        serializer = UserSubscriptionSerializer(instance.subscribed_to, context=context)
        return serializer.data

    class Meta:
        model = Subscription
        fields = (
            'subscriber',
            'subscribed_to',
        )
        read_only_fields = fields
        depth = 1