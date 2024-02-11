from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, MeViewSet

router = DefaultRouter()
router.register('me', MeViewSet)
router.register('', UserViewSet)
# # router.register('set_password', SetPasswordViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # re_path(r'auth/', include('djoser.urls.authtoken')),
]