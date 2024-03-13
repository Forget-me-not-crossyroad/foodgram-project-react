from django.contrib import admin

from .models import User, Subscription


class UserAdminPanel(admin.ModelAdmin):
    list_display = ('role', 'first_name', 'last_name',
                    'username', 'is_active', 'is_staff',
                    'is_superuser', 'email',
                    'date_joined')
    list_filter = ('username', 'email',
                   'first_name', 'last_name')
    search_fields = ('username', 'email',
                     'first_name', 'last_name')


class SubscriptionAdminPanel(admin.ModelAdmin):
    list_display = ('subscribed_to', 'subscriber')
    list_filter = ('subscribed_to', 'subscriber')
    search_fields = ('subscribed_to', 'subscriber')


admin.site.register(User, UserAdminPanel)
admin.site.register(Subscription, SubscriptionAdminPanel)
