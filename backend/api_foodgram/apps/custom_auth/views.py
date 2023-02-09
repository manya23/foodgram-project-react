from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from apps.users.models import User

from .serializers import ObtainTokenSerializer


class ObtainUserTokenView(APIView):
    # permission_classes = [AllowAny, ]
    serializer_class = ObtainTokenSerializer

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.data.get('password')
            user = get_object_or_404(User,
                                     email=request.data.get('email'))
            if password == user.password:
                print(user.email)
                return Response(get_token_for_user(user),
                                status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


def get_token_for_user(user):
    access = AccessToken.for_user(user)
    return {
        'token': str(access),
    }


# from djoser.views import UserViewSet
#
# from .serializers import CustomTokenSerializer
#
#
# class CustomTokenViewSet(UserViewSet):
#     serializer_class = CustomTokenSerializer
