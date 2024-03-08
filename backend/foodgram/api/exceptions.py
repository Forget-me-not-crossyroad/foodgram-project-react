from rest_framework.exceptions import APIException


class SubscriptionError(APIException):
    status_code = 400
    default_detail = (
        'Ошибка подписки:'
        ' подписка на самого себя/'
        ' попытка повторной подписки на того же автора.'
    )
    default_code = 'subscription_error'
