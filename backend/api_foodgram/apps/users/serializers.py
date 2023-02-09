from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    # TODO: add 'is_subscribed' to GET and remove 'password' from GET
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', )
        lookup_field = 'username'
        extra_kwargs = {
            'url': {'lookup_field': 'username'}
        }

    # TODO: add validation of field for POST
    # def validate_role(self, value):
    #     """Проверка роли, которую указал пользователь.
    #     В случае, если пользователь с ролью user прописал роль
    #     admin или moderator, принудительно устанавливаем роль user,
    #     иначе устанавливаем роль из переданной переменной."""
    #     if (value == 'admin'
    #        and get_object_or_404(User, pk=self.instance.pk).is_user):
    #         return 'user'
    #     return value


