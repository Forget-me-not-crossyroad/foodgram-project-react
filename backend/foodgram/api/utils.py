from django.apps import apps
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

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
        return modelname.objects.filter(
            **{modelfield_first: instance, modelfield_second: user_obj}
        ).exists()
    if not context.get('is_retrieve') is None:
        user = context['user_subscriber']
        user_obj = User.objects.filter(username=user).get()
        return modelname.objects.filter(
            **{modelfield_first: instance, modelfield_second: user_obj}
        ).exists()
    else:
        context = self.context['request']
        user_obj = context.user
        return modelname.objects.filter(
            **{modelfield_first: instance, modelfield_second: user_obj}
        ).exists()


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


def proccess_recipe_ingredients_data_refactor(self, instance):
    context = self.context['request']
    ingredients = context.data['ingredients']
    recipes_ingredients_bulkcreate = []
    for ingredient in ingredients:
        ingredient_for_recipe_id = ingredient['id']
        amount_for_recipe = ingredient['amount']
        recipes_ingredients_bulkcreate.append(
            IngredientRecipe(
                recipe=instance,
                amount=amount_for_recipe,
                ingredient_id=ingredient_for_recipe_id,
            )
        )
    IngredientRecipe.objects.bulk_create(recipes_ingredients_bulkcreate)


def process_perform_create(
    self, serializer, model, modelfield_first, modelfield_second
):
    modelfield_second_value = get_object_or_404(
        model, id=self.kwargs.get("recipe_id")
    )
    serializer.save(
        **{
            modelfield_first: self.request.user,
            modelfield_second: modelfield_second_value,
        }
    )


def proccess_delete(
    self,
    model_first_field,
    model_for_deletion,
    modelfield_first,
    modelfield_second,
):
    modelfield_second_value = get_object_or_404(
        model_first_field, id=self.kwargs.get("recipe_id")
    )
    instance_for_deletion = get_object_or_404(
        model_for_deletion,
        **{
            modelfield_first: self.request.user,
            modelfield_second: modelfield_second_value,
        },
    )
    instance_for_deletion.delete()
    return Response(
        {'success': 'Рецепт успешно удален из избранного.'},
        status=status.HTTP_204_NO_CONTENT,
    )
