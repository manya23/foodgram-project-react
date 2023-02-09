from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
# from .permissions import CreateListUsersPermission
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = [CreateListUsersPermission, IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    lookup_field = 'username'

    @action(detail=False,
            methods=['GET', 'PATCH', ],
            permission_classes=[IsAuthenticated, ],
            url_path='me',)
    def get_me(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        if request.method == 'GET':
            return Response(UserSerializer(user).data,
                            status=status.HTTP_200_OK)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['POST', ],
            permission_classes=[IsAuthenticated, ],
            url_path='set_password',)
    def get_set_password(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        if request.method == 'GET':
            return Response(UserSerializer(user).data,
                            status=status.HTTP_200_OK)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
