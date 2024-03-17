from django_filters import filters
from django_filters.rest_framework import BooleanFilter, FilterSet
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    author = filters.CharFilter(field_name="author", method='filter_author')
    is_favorited = BooleanFilter(method='get_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = [
            'tags',
            'author',
            'is_favorited',
        ]

    def filter_author(self, queryset, id, author):
        return queryset.filter(author=author)

    def get_favorited(self, queryset, is_favorited, *args, **kwargs):
        if not is_favorited:
            return queryset
        return queryset.filter(
            favorited_recipe__favorited_user=self.request.user
        )

    def get_is_in_shopping_cart(
        self, queryset, is_shoppingcart, *args, **kwargs
    ):
        if not is_shoppingcart:
            return queryset
        return queryset.filter(
            shoppingcart_recipe__shoppingcart_user=self.request.user
        )


class IngredientFilter(SearchFilter):
    search_param = 'name'
