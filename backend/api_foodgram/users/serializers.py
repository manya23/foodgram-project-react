from rest_framework import serializers

from users.models import User
from users.models import Follow

from djoser.serializers import (UserSerializer,
                                UserCreateSerializer)


class CustomCreateUserSerializer (UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name',)

    def to_internal_value(self, data):
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        for field in [username, first_name, last_name,
                      email, password]:
            if not field:
                raise serializers.ValidationError({
                    f'{field}': 'Обязательное поле.'
                })

        return data


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        else:
            return False

    def to_internal_value(self, data):
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        for field in [username, first_name, last_name,
                      email, password]:
            if not field:
                raise serializers.ValidationError({
                    f'{field}': 'Обязательное поле.'
                })

        return data
