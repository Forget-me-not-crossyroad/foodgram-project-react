from django.apps import apps
from django.db import models

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