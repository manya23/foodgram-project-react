from django_filters.rest_framework import (BooleanFilter, FilterSet,
                                           ModelMultipleChoiceFilter)

from users.models import User
from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     to_field_name='slug',
                                     queryset=Tag.objects.all())
    author = ModelMultipleChoiceFilter(field_name='author__id',
                                       to_field_name='id',
                                       queryset=User.objects.all())
    is_favorited = BooleanFilter(method='filter_favorited')
    is_in_shopping_cart = BooleanFilter(method='filter_in_shopping_cart')

    def filter_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            # 'ForeignKey текущей модели'__'имя поля в связанной модели'
            return queryset.filter(favorite_recipes__user=user)
        return queryset

    def filter_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            return queryset.filter(shopping_recipes__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited')
