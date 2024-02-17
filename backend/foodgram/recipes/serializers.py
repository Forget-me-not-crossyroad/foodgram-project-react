from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField

from recipes.models import Recipe, Tag, Ingredient, IngredientRecipe, IngredientAmountRecipe, Favorite, ShoppingCart


# from users.serializers import UserReadSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientAmountRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientAmountRecipe
        fields = ('id', 'amount',)


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')
    amount = serializers.IntegerField(source='amount.amount')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def to_representation(self, instance):
        ingredients = super().to_representation(instance)
        ingredients['ingredients'] = IngredientRecipeSerializer(IngredientRecipe.objects.filter(recipe=instance), many=True).data
        return ingredients

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'text', 'image', 'created', 'cooking_time', 'ingredients', 'tags',
                  'is_favorited', 'is_in_shopping_cart',)
        depth = 1

    def get_is_favorited(self, obj):
        return True

    def get_is_in_shopping_cart(self, obj):
        return True


class RecipeCreateSerializer(serializers.ModelSerializer):
    # ingredients = IngredientAmountRecipeSerializer(many=True)
    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    author = serializers.HiddenField(default=CurrentUserDefault())
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author', 'text', 'image', 'created', 'cooking_time', 'ingredients', 'tags',
                  'is_favorited', 'is_in_shopping_cart',)
        depth = 1

    def get_is_favorited(self, obj):
        return True

    def get_is_in_shopping_cart(self, obj):
        return True

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
            ingredient_for_recipe = Ingredient.objects.get(id=ingredient_for_recipe_id)
            ingredient_amount_recipe = IngredientAmountRecipe.objects.create(amount=amount_for_recipe)
            IngredientRecipe.objects.create(recipe=recipe, amount=ingredient_amount_recipe, ingredient=ingredient_for_recipe)
        recipe.tags.set(tags)
        return recipe


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
        fields = ('id', 'favorited_user', 'favorited_recipe', 'name', 'image', 'cooking_time')
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
            photo_url = Recipe.objects.get(id=obj.favorited_recipe.id).image.url
            return request.build_absolute_uri(photo_url)
        return None


class FavoriteDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('favorited_user', 'favorited_recipe',)
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
        fields = ('id', 'shoppingcart_user', 'shoppingcart_recipe', 'name', 'image', 'cooking_time')
        read_only_fields = fields
        depth = 1

    def get_name(self, obj):
        if Recipe.objects.get(id=obj.shoppingcart_recipe.id):
            return Recipe.objects.get(id=obj.shoppingcart_recipe.id).name
        return None

    def get_cooking_time(self, obj):
        if Recipe.objects.get(id=obj.shoppingcart_recipe.id):
            return Recipe.objects.get(id=obj.shoppingcart_recipe.id).cooking_time
        return None

    def get_image(self, obj):
        request = self.context.get('request')
        if Recipe.objects.get(id=obj.shoppingcart_recipe.id):
            photo_url = Recipe.objects.get(id=obj.shoppingcart_recipe.id).image.url
            return request.build_absolute_uri(photo_url)
        return None


class ShoppingCartDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('shoppingcart_user', 'shoppingcart_recipe',)
        read_only_fields = fields
        depth = 1
