from django.apps import apps
from django.db import models

from recipes.models import IngredientAmountRecipe, IngredientRecipe
from users.models import User


def proccess_custom_context(
    instance, modelfield_first, modelfield_second, self, app_name, model_name
):
    modelname = get_model_instance(app_name, model_name)
    context = self.context
    if not context.get('is_list') is None:
        user = context['user_subscriber']['username']
        user_obj = User.objects.filter(username=user).get()
        if modelname.objects.filter(
            **{modelfield_first: instance, modelfield_second: user_obj}
        ).exists():
            return True
        return False
    if not context.get('is_retrieve') is None:
        user = context['user_subscriber']
        user_obj = User.objects.filter(username=user).get()
        if modelname.objects.filter(
            **{modelfield_first: instance, modelfield_second: user_obj}
        ).exists():
            return True
        return False
    else:
        context = self.context['request']
        user_obj = context.user
        if modelname.objects.filter(
            **{modelfield_first: instance, modelfield_second: user_obj}
        ).exists():
            return True
    return False


def get_model_instance(app_name, model_name):
    return apps.get_model(f"{app_name}.{model_name}")


def proccess_recipe_ingredients_data(self, instance):
    context = self.context['request']
    ingredients = context.data['ingredients']
    recipes_ingredients_bulkcreate = []
    for ingredient in ingredients:
        ingredient_for_recipe_id = ingredient['id']
        amount_for_recipe = ingredient['amount']
        ingredient_amount_recipe = IngredientAmountRecipe.objects.create(
            amount=amount_for_recipe
        )
        recipes_ingredients_bulkcreate.append(
            IngredientRecipe(
                recipe=instance,
                amount=ingredient_amount_recipe,
                ingredient_id=ingredient_for_recipe_id,
            )
        )
    IngredientRecipe.objects.bulk_create(recipes_ingredients_bulkcreate)
