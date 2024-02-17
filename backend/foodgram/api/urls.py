from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from recipes.views import TagViewSet, IngredientViewSet, RecipeViewSet, FavoriteViewSet, ShoppingCartViewSet

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet, basename='favorites'
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart', ShoppingCartViewSet, basename='shoppingcarts'
)


urlpatterns = [
    path('users/', include('users.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]