from django.contrib import admin

from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('id', 'username', 'email')
    list_filter = ('username', 'email', )
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    empty_value_display = '-пусто-'
    list_display = ('get_author', 'get_user')

    def get_author(self, obj):
        return obj.author.username
    get_author.short_description = 'Автор'
    get_author.admin_order_field = 'author__username'

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'Подписчик'
    get_user.admin_order_field = 'user__username'
