from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from recipes.models import Recipe
from users.models import User, Follow
from users.permissions import UsersPermission
from users.serializers import CustomUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [UsersPermission, IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'id'

    @action(detail=True,
            methods=('post', 'delete',),
            permission_classes=[IsAuthenticated, ])
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['id'])
        if user == author:
            return Response({'detail': 'Нельзя подписаться на самого себя(('},
                            status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'POST':
            if not Follow.objects.filter(user=user,
                                         author=author).exists():
                Follow.objects.create(user=user,
                                      author=author)
                recipes_list = list()
                recipes_count = int()
                recipes = Recipe.objects.filter(author=author).all()
                for record in recipes:
                    recipes_list.append({
                        "id": record.recipe.id,
                        "name": record.recipe.name,
                        # "image": recipe.image,
                        "cooking_time": record.recipe.cooking_time
                    })
                    recipes_count += 1

                data = {
                    "email": author.email,
                    "id": author.id,
                    "username": author.username,
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                    "is_subscribed": Follow.objects.filter(user=user,
                                                           author=author).exists(),
                    "recipes": recipes_list,
                    "recipes_count": recipes_count
                }
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail': 'Такая запись уже существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
        elif self.request.method == 'DELETE':
            subscription_record = Follow.objects.filter(user=user,
                                                        author=author)
            if subscription_record.exists():
                subscription_record.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': 'Такой записи не существует.'},
                            status=status.HTTP_400_BAD_REQUEST)

    # http: // 127.0.0.1: 7000 / api / users / subscriptions / 2 /
    @action(detail=False,
            methods=('get',),
            url_path='subscriptions',
            permission_classes=[IsAuthenticated, ])
    def subscriptions(self, request, **kwargs):
        # TODO: опять не работает GET c detail=False (а с detail=True работает)
        user = self.request.user
        subscription_list = Follow.objects.filter(user=user).select_related('author')
        if self.request.method == 'GET':
            data = list()
            recipes_list = list()
            recipes_count = int()
            for subscription in subscription_list:
                author = subscription.author
                recipes = Recipe.objects.filter(author=author).all()
                # TODO: не отображается поле image
                for record in recipes:
                    recipes_list.append({
                        "id": record.recipe.id,
                        "name": record.recipe.name,
                        # "image": recipe.image,
                        "cooking_time": record.recipe.cooking_time
                    })
                    recipes_count += 1

                data.append({
                    "email": author.email,
                    "id": author.id,
                    "username": author.username,
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                    "is_subscribed": Follow.objects.filter(user=user,
                                                           author=author).exists(),
                    "recipes": recipes_list,
                    "recipes_count": recipes_count
                })
            return Response(data=data, status=status.HTTP_201_CREATED)
