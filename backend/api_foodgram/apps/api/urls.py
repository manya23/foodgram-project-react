from django.urls import include, path
from rest_framework import routers

from apps.users.views import UserViewSet
from apps.recipes.views import RecipeViewSet
from apps.recipes.views import TagViewSet
from apps.recipes.views import IngredientViewSet


router1 = routers.DefaultRouter()
router1.register(
    'users',
    UserViewSet,
    basename='users',
)
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
    path('', include(router1.urls)),
    # path('auth/', include('custom_auth.urls')),
]
