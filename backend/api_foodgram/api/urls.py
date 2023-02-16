from django.urls import include, path, re_path
from rest_framework import routers

from users.views import UserViewSet
from recipes.views import RecipeViewSet
from recipes.views import TagViewSet
from recipes.views import IngredientViewSet


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
    path('', include('djoser.urls')),
    path('', include(router1.urls)),

    re_path(r'^auth/', include('djoser.urls.authtoken'))
]

# from djoser.views import UserViewSet as DJUserViewSet
# ...
# path('users/set_password/',
#          DJUserViewSet.as_view({'post': 'set_password'})),
#
# urlpatterns = [
#     path('', include('djoser.urls')),
#     path('', include(v1_router.urls)),
#     path('auth/', include('djoser.urls.authtoken')),
# ]