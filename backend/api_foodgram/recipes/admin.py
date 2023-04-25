from django.contrib import admin

from .models import (Ingredient,
                     Recipe,
                     Tag,
                     IngredientRecipe,
                     TagRecipe,
                     UserFavoriteRecipe,
                     UserShoppingRecipe)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('id', 'name', 'author', )
    search_fields = ('text',)
    list_filter = ('author', 'name', 'tags', )
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('id', 'name', 'measurement_unit', )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('name', 'slug', )
    list_filter = ('color', )
    empty_value_display = '-пусто-'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(UserFavoriteRecipe)
class UserFavoriteRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'


@admin.register(UserShoppingRecipe)
class UserShoppingRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
