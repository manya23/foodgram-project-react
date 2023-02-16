from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import User

from djoser.serializers import UserSerializer, UserCreateSerializer


class CustomCreateUserSerializer (UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password',)


class CustomUserSerializer(UserSerializer,
                           serializers.ModelSerializer):
    # TODO: add 'is_subscribed' to GET and remove 'password' from GET
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password',)

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
                    f'{field}': 'This field is required.'
                })
        # self.save()
        print(data)
        print(type(data))
        # data.pop('password')
        # data.uppdate({'id': User.objects.get_object_or_404(username=username).id})

        return data


    # def to_representation(self, instance):
