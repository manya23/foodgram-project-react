import weasyprint
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView
from rest_framework.response import Response

from recipes.models import (Recipe,
                            Ingredient,
                            Tag,
                            UserFavoriteRecipe,
                            UserShoppingRecipe)
from recipes.permissions import (RecipeIsAuthenticated,
                                 FavoritesIsAuthenticated,
                                 ShoppingCartIsAuthenticated,
                                 TagIngredientPermission)
from api.serializers import (RecipeCreateSerializer,
                             RecipeRetrieveSerializer,
                             TagSerializer,
                             IngredientSerializer,
                             ShortRecipeSerializer)
from recipes.filters import RecipeFilter
from recipes.collect_pdf import collect_shopping_pdf

from users.models import (User,
                          Follow)
from users.permissions import UsersPermission


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
            RecipeRetrieveSerializer(
                instance=serializer.instance,
                context={'request': self.request}
            ).data,
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
            RecipeRetrieveSerializer(
                instance=serializer.instance,
                context={'request': self.request}
            ).data
        )

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=[IsAuthenticated, FavoritesIsAuthenticated, ])
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            UserFavoriteRecipe.objects.get_or_create(
                user=self.request.user,
                recipe=recipe
            )
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        elif request.method == 'DELETE':
            UserFavoriteRecipe.objects.filter(
                recipe=recipe,
                user=self.request.user
            ).delete()
            return Response(status=status.HTTP_200_OK)

    @action(detail=False,
            methods=('get',),
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated,
                                ShoppingCartIsAuthenticated, ])
    def get_shopping_cart(self, request, **kwargs):
        user = self.request.user
        if self.request.method == 'GET':
            shopping_cart_path = collect_shopping_pdf(user)
            shopping_cart_pdf = weasyprint.HTML(
                shopping_cart_path + '.html'
            ).write_pdf()
            filename = "shopping_card.pdf"

            response = HttpResponse(shopping_cart_pdf,
                                    content_type='application/pdf')
            response['Content-Disposition'] = ('attachment; filename="'
                                               + filename + '"')
            return response

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=[IsAuthenticated,
                                ShoppingCartIsAuthenticated, ])
    def shopping_cart(self, request, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if self.request.method == 'POST':
            # добавление рецепта в список
            UserShoppingRecipe.objects.get_or_create(
                user=user,
                recipe=recipe
            )
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        elif self.request.method == 'DELETE':
            # удаление рецепта из списка
            UserShoppingRecipe.objects.filter(
                recipe=recipe,
                user=user
            ).delete()
            return Response(status=status.HTTP_200_OK)


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    permission_classes = [TagIngredientPermission]
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request, *args, **kwargs):
        if not Tag.objects.filter(id=kwargs['pk']).exists():
            return Response(
                {'detail': 'Страница не найдена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    permission_classes = [TagIngredientPermission]
    pagination_class = None
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class UserApi(APIView):
    permission_classes = [UsersPermission, IsAuthenticated]
    pagination_class = PageNumberPagination

    def get(self, request):
        paginator = PageNumberPagination()

        user = self.request.user
        subscription_list = Follow.objects.filter(
            user=user
        ).select_related('author')
        data = list()
        recipes_list = list()
        recipes_count = int()
        for subscription in subscription_list:
            author = subscription.author
            recipes = Recipe.objects.filter(author=author).all()
            for recipe in recipes:
                serializer = ShortRecipeSerializer(
                    recipe,
                    context={'request': request}
                )
                recipes_list.append(
                    serializer.data
                )
                recipes_count += 1

            data.append({
                "email": author.email,
                "id": author.id,
                "username": author.username,
                "first_name": author.first_name,
                "last_name": author.last_name,
                "is_subscribed": Follow.objects.filter(
                    user=user,
                    author=author
                ).exists(),
                "recipes": recipes_list,
                "recipes_count": recipes_count
            })
        result_page = paginator.paginate_queryset(data, request)
        return paginator.get_paginated_response(result_page)


@api_view(['POST', 'DELETE', ])
@permission_classes([IsAuthenticated, ])
def subscribe(request, user_id):
    user = request.user
    author = get_object_or_404(User, id=user_id)
    if user == author:
        return Response({'detail': 'Нельзя подписаться на самого себя(('},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        Follow.objects.get_or_create(
            user=user,
            author=author
        )
        recipes_list = list()
        recipes_count = int()
        recipes = Recipe.objects.filter(author=author).all()
        for recipe in recipes:
            serializer = ShortRecipeSerializer(
                recipe,
                context={'request': request}
            )
            recipes_list.append(
                serializer.data
            )
            recipes_count += 1

        data = {
            "email": author.email,
            "id": author.id,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
            "is_subscribed": Follow.objects.filter(
                user=user,
                author=author
            ).exists(),
            "recipes": recipes_list,
            "recipes_count": recipes_count
        }
        return Response(data=data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        Follow.objects.filter(
            user=user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
