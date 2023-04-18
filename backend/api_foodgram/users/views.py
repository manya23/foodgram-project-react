from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from recipes.models import Recipe
from users.models import User, Follow
from users.permissions import UsersPermission


@api_view(['POST', 'DELETE', ])
@permission_classes([IsAuthenticated, ])
def subscribe(request, user_id):
    user = request.user
    author = get_object_or_404(User, id=user_id)
    if user == author:
        return Response({'detail': 'Нельзя подписаться на самого себя(('},
                        status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
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
                    "cooking_time": record.recipe.cooking_time
                })
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
        else:
            return Response({'detail': 'Такая запись уже существует.'},
                            status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        subscription_record = Follow.objects.filter(user=user,
                                                    author=author)
        if subscription_record.exists():
            subscription_record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'Такой записи не существует.'},
                        status=status.HTTP_400_BAD_REQUEST)


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
            # TODO: не отображается поле image
            for record in recipes:
                recipes_list.append({
                    "id": record.recipe.id,
                    "name": record.recipe.name,
                    "cooking_time": record.recipe.cooking_time
                })
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
