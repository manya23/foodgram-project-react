from rest_framework import permissions


class RecipeIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        # гет доступен всем: поставлю ReadOnly
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # пост только авторизованным польззователям
        # патч и делит доступен только автору рецепта
        if (
                request.method in ['DELETE', 'PATCH', ]
                and request.user.is_user
                and request.user != obj.author
        ):
            return False
        return True


class FavoritesIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ['POST', 'DELETE']
            and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # только авторизованному пользователю
        return request.user.is_authenticated


class ShoppingCartIsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.method in ['POST', 'DELETE']
            and request.user.is_authenticated
        )


class TagIngredientPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
        )
