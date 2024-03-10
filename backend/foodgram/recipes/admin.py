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


admin.site.register(Ingredient, IngredientAdminPanel)
admin.site.register(Tag, TagAdminPanel)
