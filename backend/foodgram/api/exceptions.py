from rest_framework.exceptions import APIException


class SubscriptionError(APIException):
    status_code = 400
    default_detail = (
        'Ошибка подписки:'
        ' подписка на самого себя'
        ' попытка повторной подписки на того же автора.'
    )
    default_code = 'subscription_error'


class IngredientRecipeCreateUpdateError(APIException):
    status_code = 400
    default_detail = (
        'Ошибка создания/редактирования рецепта:'
        ' рецепт не может содержать'
        ' дублирующихся ингредиентов. '
        'Удалите дублирующиеся ингредиенты'
    )
    default_code = 'recipe_create_update_error'


class RecipeCreateUpdateError(APIException):
    status_code = 400
    default_detail = (
        'Ошибка создания/редактирования рецепта:'
        ' один и тот же автор не может создать два'
        'рецепта с одинаковым названием'
    )
    default_code = 'recipe_create_update_error'
