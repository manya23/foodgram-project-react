from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import Recipe, Ingredient, Tag, UserFavoriteRecipe, UserShoppingRecipe
from recipes.permissions import (RecipeIsAuthenticated, FavoritesIsAuthenticated,
                                 ShoppingCartIsAuthenticated, TagIngredientPermission)
from recipes.serializers import (RecipeCreateSerializer, RecipeRetrieveSerializer,
                                 TagSerializer, IngredientSerializer)
from recipes.filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (RecipeIsAuthenticated, IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all()
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('tags',)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list',):
            return RecipeRetrieveSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            RecipeRetrieveSerializer(instance=serializer.instance,
                                     context={'request': self.request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(
            RecipeRetrieveSerializer(instance=serializer.instance,
                                     context={'request': self.request}).data
        )

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=[IsAuthenticated, FavoritesIsAuthenticated, ])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        print(recipe.name, '\n', recipe.cooking_time)
        if request.method == 'POST':
            # recipes = user.following.select_related('recipe').all()
            if not UserFavoriteRecipe.objects.filter(user=self.request.user,
                                                     recipe=recipe).exists():
                ##################################
                # В случае GET-запроса возвращаем список всех котиков
                # cats = Cat.objects.all()
                # serializer = CatSerializer(cats, many=True)
                # return Response(serializer.data)

                # serializer = ShortRecipeSerializer(
                #     recipe,
                #     data=request.data,
                #     context={'request': request}
                # )
                # print(serializer.initial_data)
                # if serializer.is_valid(raise_exception=True):
                #     print(serializer.data)
                #     UserFavoriteRecipe.objects.create(user=self.request.user,
                #                                       recipe=recipe)
                #     return Response(serializer.data,
                #                     status=status.HTTP_201_CREATED)
                ##################################
                UserFavoriteRecipe.objects.create(user=self.request.user,
                                                  recipe=recipe)
                data = {
                    "id": recipe.id,
                    "name": recipe.name,
                    # "image": recipe.image,
                    "cooking_time": recipe.cooking_time
                }
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Такая запись уже существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user_fav_recipe_record = get_object_or_404(UserFavoriteRecipe,
                                                       recipe=recipe,
                                                       user=self.request.user)
            user_fav_recipe_record.delete()
            return Response(status=status.HTTP_200_OK)

    @action(detail=False,
            methods=('get',),
            url_path='shopping_cart',
            permission_classes=[IsAuthenticated, ShoppingCartIsAuthenticated, ])
    def get_shopping_cart(self, request, **kwargs):
        user = self.request.user
        if self.request.method == 'GET':
            # сборка списка из ингредиентов всех рецептов в списке
            shopping_list = list()
            recipes = UserShoppingRecipe.objects.filter(user=user).select_related('recipe')
            for record in recipes:
                shopping_list.append({
                    "id": record.recipe.id,
                    "name": record.recipe.name,
                    # "image": recipe.image,
                    "cooking_time": record.recipe.cooking_time
                })
            # TODO: возвращаю пдф со списком покупок
            print('List empty')
            return Response(data=shopping_list, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=[IsAuthenticated, ShoppingCartIsAuthenticated, ])
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        if self.request.method == 'POST':
            # добавление рецепта в список
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            if not UserShoppingRecipe.objects.filter(user=user,
                                                     recipe=recipe).exists():
                UserShoppingRecipe.objects.create(user=user,
                                                  recipe=recipe)
                data = {
                    "id": recipe.id,
                    "name": recipe.name,
                    # "image": recipe.image,
                    "cooking_time": recipe.cooking_time}
                return Response(data=data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Такая запись уже существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif self.request.method == 'DELETE':
            # удаление рецепта из списка
            recipe = get_object_or_404(Recipe, id=kwargs['pk'])
            shopping_list_recipe_record = get_object_or_404(UserShoppingRecipe,
                                                            recipe=recipe,
                                                            user=user)
            shopping_list_recipe_record.delete()
            return Response(status=status.HTTP_200_OK)


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = [TagIngredientPermission]
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
    permission_classes = [TagIngredientPermission]
    # TODO: get - ингредиентов с возможностью поиска по имени
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
