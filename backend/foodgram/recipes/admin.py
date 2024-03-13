from django.contrib import admin

from .models import (Ingredient, IngredientRecipe, Tag)


class IngredientsInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 4


class TagAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientAdminPanel(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientRecipeAdminPanel(admin.ModelAdmin):
    list_display = ('id', 'recipe',
                    'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')
    search_fields = ('name', 'id')

class FavoriteAdminPanel(admin.ModelAdmin):
    list_display = ('favorited_user', 'favorited_recipe')
    list_filter = ('favorited_user', 'favorited_recipe')
    search_fields = ('favorited_user', 'favorited_recipe')


class ShoppingCartAdminPanel(admin.ModelAdmin):
    list_display = ('shoppingcart_user', 'shoppingcart_recipe')
    list_filter = ('shoppingcart_user', 'shoppingcart_recipe')
    search_fields = ('shoppingcart_user', 'shoppingcart_recipe')





admin.site.register(Ingredient, IngredientAdminPanel)
admin.site.register(Tag, TagAdminPanel)
