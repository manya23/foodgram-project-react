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
                             ShortRecipeSerializer,
                             SubscriptionSerializer)
from recipes.filters import RecipeFilter
from recipes.collect_pdf import collect_shopping_pdf
from users.models import (User,
                          Follow)
from users.permissions import UsersPermission


class BaseGetView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin
):
    pass


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

    @action(detail=True,
            methods=('post', 'delete'),
            permission_classes=[IsAuthenticated,
                                FavoritesIsAuthenticated, ])
    def favorite(self, request, **kwargs):
        return add_or_delete_user_recipe_connection(
            self,
            UserFavoriteRecipe,
            request,
            kwargs['pk']
        )

    @action(detail=False,
            methods=('get',),
            url_path='download_shopping_cart',
            permission_classes=[IsAuthenticated,
                                ShoppingCartIsAuthenticated, ])
    def get_shopping_cart(self, request, **kwargs):
        user = self.request.user
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
        return add_or_delete_user_recipe_connection(
            self,
            UserShoppingRecipe,
            request,
            kwargs['pk']
        )


class TagViewSet(BaseGetView):
    permission_classes = [TagIngredientPermission]
    pagination_class = None
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseGetView):
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
        serializer = SubscriptionSerializer(
            subscription_list,
            context={'request': request},
            many=True
        )
        result_page = paginator.paginate_queryset(serializer.data, request)
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
        subscription, _ = Follow.objects.get_or_create(
            user=user,
            author=author
        )
        serializer = SubscriptionSerializer(
            subscription,
            context={'request': request},
        )
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        Follow.objects.filter(
            user=user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def add_or_delete_user_recipe_connection(
        viewset_object,
        connection_model,
        request,
        pk
):
    user = viewset_object.request.user
    recipe = get_object_or_404(Recipe, id=pk)
    if viewset_object.request.method == 'POST':
        # добавление рецепта в список
        connection_model.objects.get_or_create(
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
    elif viewset_object.request.method == 'DELETE':
        # удаление рецепта из списка
        connection_model.objects.filter(
            recipe=recipe,
            user=user
        ).delete()
        return Response(status=status.HTTP_200_OK)
