import io

from django.db.models import Sum, IntegerField
from django.db.models.functions import Cast
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from api.pagination import TruncatedListPagination
from users.models import Subscription, User
from foodgram import settings
from foodgram.permission import OwnerOrReadOnly
from recipes.models import (
    Favorite,
    Ingredient,
    IngredientRecipe,
    Recipe,
    ShoppingCart,
    Tag,
)
from api.filters import RecipeFilter, IngredientFilter
from api.serializers import (
    FavoriteDeleteSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    MeReadSerializer,
    RecipeCreateUpdateSerializer,
    RecipeReadSerializer,
    ShoppingCartDeleteSerializer,
    ShoppingCartSerializer,
    SubscriptionDeleteSerializer,
    SubscriptionSerializer,
    SubscriptionsSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserReadSerializer,
)
from api.utils import process_delete, process_perform_create


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    pagination_class = None
    filter_backends = (IngredientFilter,)
    search_fields = ['^name']


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
        return RecipeCreateUpdateSerializer


class FavoriteViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None

    def get_queryset(self):
        return self.request.user.favorited_user.all()

    def get_serializer_class(self):
        if self.action in ('delete',):
            return FavoriteDeleteSerializer
        return FavoriteSerializer

    def perform_create(self, serializer):
        process_perform_create(
            self=self,
            serializer=serializer,
            model=Recipe,
            modelfield_first='favorited_user',
            modelfield_second='favorited_recipe',
        )

    def delete(self, request, *args, **kwargs):
        return process_delete(
            self=self,
            model_first_field=Recipe,
            model_for_deletion=Favorite,
            modelfield_first='favorited_user',
            modelfield_second='favorited_recipe',
        )


class ShoppingCartViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None

    def get_queryset(self):
        return self.request.user.shoppingcart_user.all()

    def get_serializer_class(self):
        if self.action in ('delete',):
            return ShoppingCartDeleteSerializer
        return ShoppingCartSerializer

    def perform_create(self, serializer):
        process_perform_create(
            self=self,
            serializer=serializer,
            model=Recipe,
            modelfield_first='shoppingcart_user',
            modelfield_second='shoppingcart_recipe',
        )

    def delete(self, request, *args, **kwargs):
        return process_delete(
            self=self,
            model_first_field=Recipe,
            model_for_deletion=ShoppingCart,
            modelfield_first='shoppingcart_user',
            modelfield_second='shoppingcart_recipe',
        )


class ShoppingCartDownloadView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        return self.download_shoppingcart(request, request.user)

    def download_shoppingcart(self, request, user):
        shoppingcart_ingredients_list = []
        recipe_ingredient_amount_queryset = (
            IngredientRecipe.objects.filter(
                recipe__shoppingcart_recipe__shoppingcart_user=user
            )
            .values('ingredient__name', 'ingredient__measurement_unit')
            .distinct()
            .annotate(amounts=Sum(Cast('amount', IntegerField())))
            .order_by('amounts')
        )

        for item in recipe_ingredient_amount_queryset:
            shoppingcart_ingredients_list.append(
                f'{item["ingredient__name"]}'
                f' - {item["amounts"]} {item["ingredient__measurement_unit"]}'
            )

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
        for i in range(0, len(shoppingcart_ingredients_list)):
            if y < 60:
                p.showPage()
                p.setFont("FreeSans", 12)
                y = 800
            if i == 0:
                p.drawCentredString(
                    4.25 * inch, y, shoppingcart_ingredients_list[i]
                )
                y -= 60
            else:
                p.drawCentredString(
                    4.25 * inch, y, shoppingcart_ingredients_list[i]
                )
                y -= 60
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
            return UserReadSerializer
        return UserCreateSerializer

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
    queryset = User.objects.all()
    serializer_class = MeReadSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None
    pagination_class = None

    def get_queryset(self):
        user_id = self.request.user.id
        return User.objects.filter(id=user_id)

    def list(self, request, *args, **kwargs):
        serializer = MeReadSerializer(self.get_queryset(), many=True)
        return Response(serializer.data[0])


class SubscriptionViewSet(CreateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    throttle_scope = None

    def get_queryset(self):
        return self.request.user.subscriber.all()

    def get_serializer_class(self):
        if self.action in ('delete',):
            return SubscriptionDeleteSerializer
        return SubscriptionSerializer

    def perform_create(self, serializer):
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
        serializer.save(
            subscriber=self.request.user, subscribed_to=subscribed_to
        )

    def delete(self, request, *args, **kwargs):
        subscribed_to = get_object_or_404(User, id=self.kwargs.get("user_id"))
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
    pagination_class = TruncatedListPagination
    throttle_scope = None

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)
