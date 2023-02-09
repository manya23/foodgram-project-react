from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'password', )
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }

    # def validate_role(self, value):
    #     """Проверка роли, которую указал пользователь.
    #     В случае, если пользователь с ролью user прописал роль
    #     admin или moderator, принудительно устанавливаем роль user,
    #     иначе устанавливаем роль из переданной переменной."""
    #     if (value == 'admin'
    #        and get_object_or_404(User, pk=self.instance.pk).is_user):
    #         return 'user'
    #     return value
