from django.shortcuts import get_object_or_404
from rest_framework import serializers
from apps.users.models import User


class ObtainTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'password')

    # для записи
    # TODO: а почему тут не через validate ?
    def to_internal_value(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email:
            raise serializers.ValidationError({
                'email': 'This field is required.'
            })

        if password != get_object_or_404(
                User, email=email).password:
            raise serializers.ValidationError({
                'password': 'wrong password.'
            })

        return data


# from djoser.serializers import TokenSerializer
#
# from apps.users.models import User
#
#
# class CustomTokenSerializer(TokenSerializer):
#     class Meta(TokenSerializer.Meta):
#         model = User
#         fields = ('password', 'email', )
