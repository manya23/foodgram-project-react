from django.contrib import admin
from django.db.models import Count

from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag,
                            TagRecipe, UserFavoriteRecipe, UserShoppingRecipe)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('id', 'name', 'author', 'get_recipes_count')
    search_fields = ('text',)
    list_filter = ('author', 'name', 'tags', )
    empty_value_display = '-пусто-'

    def get_recipes_count(self, obj):
        return obj.recipes_count
    get_recipes_count.short_description = 'Добавление рецепта в избранное'

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            recipes_count=Count("favorite_recipes"),
        )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('id', 'name', 'measurement_unit', )
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(IngredientRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('amount', 'get_recipe', 'get_ingredient')

    def get_recipe(self, obj):
        return obj.recipe.name
    get_recipe.short_description = 'Рецепт'
    get_recipe.admin_order_field = 'recipe__name'

    def get_ingredient(self, obj):
        return obj.ingredient.name
    get_ingredient.short_description = 'Ингредиент'
    get_ingredient.admin_order_field = 'ingredient__name'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Создание объекта для настройки параметров админки."""
    list_display = ('name', 'slug', )
    list_filter = ('color', )
    empty_value_display = '-пусто-'


@admin.register(TagRecipe)
class TagRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('get_recipe', 'get_tag')

    def get_recipe(self, obj):
        return obj.recipe.name
    get_recipe.short_description = 'Рецепт'
    get_recipe.admin_order_field = 'recipe__name'

    def get_tag(self, obj):
        return obj.tag.name
    get_tag.short_description = 'Тэг'
    get_tag.admin_order_field = 'tag__name'


@admin.register(UserFavoriteRecipe)
class UserFavoriteRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('get_recipe', 'get_user')

    def get_recipe(self, obj):
        return obj.recipe.name
    get_recipe.short_description = 'Рецепт'
    get_recipe.admin_order_field = 'recipe__name'

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'Пользователь'
    get_user.admin_order_field = 'user__username'


@admin.register(UserShoppingRecipe)
class UserShoppingRecipeAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
    list_display = ('get_recipe', 'get_user')

    def get_recipe(self, obj):
        return obj.recipe.name
    get_recipe.short_description = 'Рецепт'
    get_recipe.admin_order_field = 'recipe__name'

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'Пользователь'
    get_user.admin_order_field = 'user__username'
