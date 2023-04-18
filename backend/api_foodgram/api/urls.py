from django.urls import include, path
from rest_framework import routers

from users.views import UserApi, subscribe
from recipes.views import RecipeViewSet
from recipes.views import TagViewSet
from recipes.views import IngredientViewSet


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
    path('users/subscriptions/', UserApi.as_view()),
    path('users/<int:user_id>/subscribe/', subscribe),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router1.urls)),
]
