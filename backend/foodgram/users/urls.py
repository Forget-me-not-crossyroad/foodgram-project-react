from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, MeViewSet, SetPasswordViewSet, SubscriptionViewSet, SubscriptionsViewSet

router = DefaultRouter()
router.register('me', MeViewSet)
router.register('set_password', SetPasswordViewSet)
router.register('subscriptions', SubscriptionsViewSet)
router.register(
    r'(?P<user_id>\d+)/subscribe', SubscriptionViewSet, basename='subscriptions'
)
router.register('', UserViewSet)



urlpatterns = [
    path('', include(router.urls)),
]