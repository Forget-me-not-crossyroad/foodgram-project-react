from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from api.views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                       ShoppingCartDownloadView, ShoppingCartViewSet,
                       TagViewSet)

router = DefaultRouter()
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('recipes', RecipeViewSet)
router.register(
    r'recipes/(?P<recipe_id>\d+)/favorite',
    FavoriteViewSet,
    basename='favorites',
)
router.register(
    r'recipes/(?P<recipe_id>\d+)/shopping_cart',
    ShoppingCartViewSet,
    basename='shoppingcarts',
)


urlpatterns = [
    path('users/', include('users.urls')),
    re_path(r'auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownloadView.as_view(),
        name='download_shopping_cart',
    ),
    path('', include(router.urls)),
]
