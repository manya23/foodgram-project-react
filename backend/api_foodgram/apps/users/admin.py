from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('username',)
    search_fields = ('username',)
    empty_value_display = '-пусто-'
