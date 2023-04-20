from django.urls import include, path
from rest_framework import routers

from api.views import UserApi, subscribe
from api.views import RecipeViewSet
from api.views import TagViewSet
from api.views import IngredientViewSet


router1 = routers.DefaultRouter()
router1.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router1.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router1.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path(
        'users/subscriptions/',
        UserApi.as_view(),
        name='users_subscriptions'
    ),
    path(
        'users/<int:user_id>/subscribe/',
        subscribe,
        name='create_user_subscription'
    ),
    path(
        '',
        include('djoser.urls')
    ),
    path(
        'auth/',
        include('djoser.urls.authtoken')
    ),
    path(
        '',
        include(router1.urls)
    ),
]
