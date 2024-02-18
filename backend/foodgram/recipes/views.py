import io

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, \
    UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart, IngredientRecipe
from recipes.serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer, RecipeCreateSerializer, \
    FavoriteSerializer, FavoriteDeleteSerializer, ShoppingCartSerializer, ShoppingCartDeleteSerializer


class TagViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    pagination_class = None

    def retrieve(self, request, *args, **kwargs):
        if not Tag.objects.filter(id=self.kwargs.get('pk')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        super().retrieve(request, *args, **kwargs)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    SearchFilter.search_param = 'name'
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ['name']


class RecipeViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            serializer_class = RecipeReadSerializer
        else:
            serializer_class = RecipeCreateSerializer
        return serializer_class


class FavoriteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None

    def get_queryset(self):
        return self.request.user.favorited_user.all()

    def get_serializer_class(self):
        if self.action in ('delete',):
            serializer_class = FavoriteDeleteSerializer
        else:
            serializer_class = FavoriteSerializer
        return serializer_class

    def perform_create(self, serializer):
        favorited_recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        serializer.save(favorited_user=self.request.user, favorited_recipe=favorited_recipe)

    def delete(self, request, *args, **kwargs):
        if not Recipe.objects.filter(id=self.kwargs.get('recipe_id')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        favorited_recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        if not Favorite.objects.filter(favorited_user=self.request.user, favorited_recipe=favorited_recipe).exists():
            return Response(
                {'errors': 'Ошибка удаления из избранного (рецепт не был в избранном)'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorited = get_object_or_404(Favorite, favorited_user=self.request.user, favorited_recipe=favorited_recipe)
        favorited.delete()
        return Response({'success': 'Рецепт успешно удален из избранного.'}, status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None

    def get_queryset(self):
        return self.request.user.shoppingcart_user.all()

    def get_serializer_class(self):
        if self.action in ('delete',):
            serializer_class = ShoppingCartDeleteSerializer
        else:
            serializer_class = ShoppingCartSerializer
        return serializer_class

    def perform_create(self, serializer):
        shoppingcart_recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        serializer.save(shoppingcart_user=self.request.user, shoppingcart_recipe=shoppingcart_recipe)

    def delete(self, request, *args, **kwargs):
        if not Recipe.objects.filter(id=self.kwargs.get('recipe_id')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        shoppingcart_recipe = get_object_or_404(Recipe, id=self.kwargs.get("recipe_id"))
        if not ShoppingCart.objects.filter(shoppingcart_user=self.request.user, shoppingcart_recipe=shoppingcart_recipe).exists():
            return Response(
                {'errors': 'Ошибка удаления из корзины (рецепт не был в корзине)'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        shoppingcart = get_object_or_404(ShoppingCart, shoppingcart_user=self.request.user, shoppingcart_recipe=shoppingcart_recipe)
        shoppingcart.delete()
        return Response({'success': 'Рецепт успешно удален из корзины.'}, status=status.HTTP_204_NO_CONTENT)


class ShoppingCartDownloadView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        user = request.user
        return self.download_shoppingcart(request, user)

    def download_shoppingcart(self, request, user):

        ingredients_set = set({})
        string_list = []

        recipes_list = []
        for shopping_cart in ShoppingCart.objects.filter(shoppingcart_user=user):
            recipes_list.append(shopping_cart.shoppingcart_recipe)

        for shoppingcart_recipe in recipes_list:
            for ingredient_recipe in IngredientRecipe.objects.filter(recipe=shoppingcart_recipe):
                ingredients_set.add(ingredient_recipe.ingredient.id)

        for ingredient in ingredients_set:
            amount = 0
            for ingredient_recipe_item in IngredientRecipe.objects.filter(recipe__shoppingcart_recipe__shoppingcart_user=user, ingredient_id=ingredient):
                amount += int(ingredient_recipe_item.amount.amount)
            name = Ingredient.objects.get(id=ingredient).name
            measurement_unit = Ingredient.objects.get(id=ingredient).measurement_unit
            string_list.append(f'{name} - {amount} {measurement_unit}')

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica", 12)

        y = 800
        for i in range(0, len(string_list)):
            if i == 0:
                p.drawCentredString(4.25*inch, y, string_list[i])
                y -= 60
            else:
                p.drawCentredString(4.25 * inch, y, string_list[i])
                y -= 60
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="cart_list.pdf")
