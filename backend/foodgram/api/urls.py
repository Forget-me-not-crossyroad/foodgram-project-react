from django.urls import include, path, re_path


urlpatterns = [
    path('users/', include('users.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]