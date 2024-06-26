from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from djoser import views

from api.views import (
    FavoriteViewSet,
    IngredientViewSet,
    MeViewSet,
    RecipeViewSet,
    ShoppingCartDownloadView,
    ShoppingCartViewSet,
    SubscriptionsViewSet,
    SubscriptionViewSet,
    TagViewSet,
    UserViewSet,
)

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
router.register('users/me', MeViewSet)
router.register('users/subscriptions', SubscriptionsViewSet)
router.register('users', UserViewSet)
router.register(
    r'users/(?P<user_id>\d+)/subscribe',
    SubscriptionViewSet,
    basename='subscriptions',
)


urlpatterns = [
    re_path(r'auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/download_shopping_cart/',
        ShoppingCartDownloadView.as_view(),
        name='download_shopping_cart',
    ),
    path(
        'users/set_password/',
        views.UserViewSet.as_view({"post": "set_password"}),
        name="set_password",
    ),
    path('', include(router.urls)),
]
