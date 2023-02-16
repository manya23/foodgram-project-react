from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import User
# from .permissions import CreateListUsersPermission
from .serializers import CustomUserSerializer


class UserViewSet(viewsets.ModelViewSet):
    # permission_classes = [CreateListUsersPermission, IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'id'

