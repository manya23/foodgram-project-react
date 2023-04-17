import re
from rest_framework import permissions


class UsersPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        # if re.search('api/users/$', request.stream.path) and request.method == 'POST':
        #     return True
        return (
                (request.method in permissions.SAFE_METHODS
                 or request.method == 'POST')
                and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # if re.search('api/users/$', request) and request.method == 'POST':
        #     return True
        return (
                (request.method in permissions.SAFE_METHODS
                 or request.method == 'POST')
                or request.user.is_admin
        )
