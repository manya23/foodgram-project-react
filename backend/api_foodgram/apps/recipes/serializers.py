from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import Recipe, Tag, Ingredient


class RecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name',
                  'image', 'text', 'cooking_time', )
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug', )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', )
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }