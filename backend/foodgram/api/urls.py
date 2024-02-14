from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
# router.register('recipes', RecipeViewSet)


urlpatterns = [
    path('users/', include('users.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]