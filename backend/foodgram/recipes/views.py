from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter, BaseFilterBackend
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from recipes.models import Tag, Ingredient, Recipe
from recipes.serializers import TagSerializer, IngredientSerializer, RecipeReadSerializer, RecipeCreateSerializer


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


class RecipeViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (AllowAny,)
    throttle_scope = None
    # pagination_class = None

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            serializer_class = RecipeReadSerializer
        else:
            serializer_class = RecipeCreateSerializer
        return serializer_class