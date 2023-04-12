from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response

from .models import Recipe, Ingredient, Tag, UserFavoriteRecipe
# from .permissions import CreateListUsersPermission
from .serializers import RecipeCreateSerializer, RecipeRetrieveSerializer, TagSerializer, IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    # permission_classes = [CreateListUsersPermission, IsAuthenticated]
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('tags', )

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list',):
            print('action is: ', self.action)
            return RecipeRetrieveSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            # recipes = user.following.select_related('recipe').all()
            # recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            UserFavoriteRecipe.objects.create(user=self.request.user,
                                              recipe=recipe)
            data = {
                    "id": recipe.id,
                    "name": recipe.name,
                    # "image": recipe.image,
                    "cooking_time": recipe.cooking_time
                }
            return Response(data=data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            user_fav_recipe_record = get_object_or_404(UserFavoriteRecipe,
                                                       recipe=recipe,
                                                       user=self.request.user)
            user_fav_recipe_record.delete()
            return Response(status=status.HTTP_200_OK)


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    # permission_classes = [CreateListUsersPermission, IsAuthenticated]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request, *args, **kwargs):
        if not Tag.objects.filter(id=kwargs['pk']).exists():
            return Response({'detail': 'Страница не найдена.'},
                            status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    # permission_classes = [CreateListUsersPermission, IsAuthenticated]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
