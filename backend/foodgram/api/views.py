import io

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django_filters import filters
from django_filters.rest_framework import (BooleanFilter, DjangoFilterBackend,
                                           FilterSet)

from api.filters import RecipeFilter
from foodgram import settings
from foodgram.permission import OwnerOrReadOnly
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin, DestroyModelMixin,
                                   ListModelMixin, RetrieveModelMixin,
                                   UpdateModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet, ModelViewSet
from users.models import Me, SetPassword, Subscription, User

from api.serializers import (FavoriteDeleteSerializer, FavoriteSerializer,
                             IngredientSerializer, MeReadSerializer,
                             RecipeCreateUpdateSerializer, RecipeReadSerializer,
                             SetPasswordSerializer,
                             ShoppingCartDeleteSerializer,
                             ShoppingCartSerializer,
                             SubscriptionDeleteSerializer,
                             SubscriptionSerializer, SubscriptionsSerializer,
                             TagSerializer, UserCreateSerializer,
                             UserReadSerializer)
from api.utils import process_perform_create, proccess_delete


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    SearchFilter.search_param = 'name'
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    pagination_class = None
    filter_backends = (SearchFilter,)
    search_fields = ['name']


class RecipeViewSet(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    GenericViewSet,
    DestroyModelMixin,
):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (OwnerOrReadOnly,)
    throttle_scope = None
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        else:
            return RecipeCreateUpdateSerializer


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
            return FavoriteDeleteSerializer
        else:
            return FavoriteSerializer

    def perform_create(self, serializer):
        process_perform_create(
            self=self, serializer=serializer,
            model=Recipe, modelfield_first='favorited_user',
            modelfield_second='favorited_recipe')

    def delete(self, request, *args, **kwargs):
        return proccess_delete(
         self=self, model_first_field=Recipe,
         model_for_deletion=Favorite, modelfield_first='favorited_user',
         modelfield_second='favorited_recipe'
        )


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
            return ShoppingCartDeleteSerializer
        else:
            return ShoppingCartSerializer

    def perform_create(self, serializer):
        process_perform_create(
            self=self, serializer=serializer,
            model=Recipe, modelfield_first='shoppingcart_user',
            modelfield_second='shoppingcart_recipe')

    def delete(self, request, *args, **kwargs):
        return proccess_delete(
            self=self, model_first_field=Recipe,
            model_for_deletion=ShoppingCart, modelfield_first='shoppingcart_user',
            modelfield_second='shoppingcart_recipe'
        )


class ShoppingCartDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        return self.download_shoppingcart(request, user)

    def download_shoppingcart(self, request, user):

        ingredients_set = set({})
        string_list = []

        recipes_list = []
        for shopping_cart in ShoppingCart.objects.filter(
            shoppingcart_user=user
        ):
            recipes_list.append(shopping_cart.shoppingcart_recipe)

        for shoppingcart_recipe in recipes_list:
            for ingredient_recipe in IngredientRecipe.objects.filter(
                recipe=shoppingcart_recipe
            ):
                ingredients_set.add(ingredient_recipe.ingredient.id)

        for ingredient in ingredients_set:
            amount = 0
            for ingredient_recipe_item in IngredientRecipe.objects.filter(
                recipe__shoppingcart_recipe__shoppingcart_user=user,
                ingredient_id=ingredient,
            ):
                amount += int(ingredient_recipe_item.amount.amount)
            name = Ingredient.objects.get(id=ingredient).name
            measurement_unit = Ingredient.objects.get(
                id=ingredient
            ).measurement_unit
            string_list.append(f'{name} - {amount} {measurement_unit}')

        pdfmetrics.registerFont(
            TTFont(
                'FreeSans',
                str(settings.BASE_DIR) + '/recipes/static/FreeSans.ttf',
                'UTF-8',
            )
        )
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("FreeSans", 12)

        y = 800
        for i in range(0, len(string_list)):
            if i == 0:
                p.drawCentredString(4.25 * inch, y, string_list[i])
                y -= 60
            else:
                p.drawCentredString(4.25 * inch, y, string_list[i])
                y -= 60
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename="cart_list.pdf"
        )


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
            return Response(
                {'success': 'Пароль успешно изменен.'},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Http404:
            return Response(
                {'errors': 'Введен неверный существующий пароль.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
            return SubscriptionDeleteSerializer
        else:
            return SubscriptionSerializer

    def perform_create(self, serializer):
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
        serializer.save(
            subscriber=self.request.user, subscribed_to=subscribed_to
        )

    def delete(self, request, *args, **kwargs):
        if not User.objects.filter(id=self.kwargs.get('user_id')).exists():
            return Response(
                {'errors': 'Объект не найден'},
                status=status.HTTP_404_NOT_FOUND,
            )
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
        if not Subscription.objects.filter(
            subscriber=self.request.user, subscribed_to=subscribed_to
        ).exists():
            return Response(
                {'errors': ' Ошибка отписки (пользователь не был подписан)'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription = get_object_or_404(
            Subscription,
            subscriber=self.request.user,
            subscribed_to=subscribed_to,
        )
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

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)
