from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet, MeViewSet

# router = DefaultRouter()
# router.register('', UserViewSet)
# router.register('me', MeViewSet)
# # router.register('set_password', SetPasswordViewSet)
# path('/', include('users.urls')),


# urlpatterns = [
#     path('', include(router.urls)),
#     # re_path(r'auth/', include('djoser.urls.authtoken')),
# ]

urlpatterns = [
    path('users/', include('users.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]