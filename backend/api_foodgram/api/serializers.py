from api.fields import Base64ImageField
from api.utils import create_recipe_record
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import (Ingredient, IngredientRecipe, Recipe, Tag,
                            UserFavoriteRecipe, UserShoppingRecipe)
from rest_framework import serializers, validators
from users.models import Follow, User


class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password',)

    def to_representation(self, instance):
        return UserCreateRetrieveSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data


class UserCreateRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(user=self.context['request'].user,
                                         author=obj).exists()
        return False


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }


class IngredientRecipeInputSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient_id")
    amount = serializers.IntegerField()


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientRecipeInputSerializer(many=True,
                                                  source='ingredientrecipe')
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['tags', 'ingredients', 'name',
                  'text', 'cooking_time', 'image']
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Recipe.objects.all(),
                fields=('tags', 'ingredients', 'name',
                        'text', 'cooking_time')
            )
        ]

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredientrecipe')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)

        create_recipe_record(
            ingredients,
            recipe,
            tags
        )
        return recipe

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        ingredients = validated_data.pop('ingredientrecipe')
        tags = validated_data.pop('tags')

        IngredientRecipe.objects.filter(recipe=instance).delete()

        create_recipe_record(
            ingredients,
            instance,
            tags
        )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeRetrieveSerializer(
            instance=instance,
            context={'request': self.context.get('request')}
        ).data


class RecipeRetrieveSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True,
                         read_only=True)
    ingredients = IngredientRecipeSerializer(source='ingredientrecipe_set',
                                             many=True,
                                             read_only=True)
    image = Base64ImageField(required=False, allow_null=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'author',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'text', 'cooking_time', 'image',)
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }
        depth = 2

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        recipe = get_object_or_404(Recipe, id=obj.id)
        return UserFavoriteRecipe.objects.filter(recipe=recipe,
                                                 user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        recipe = get_object_or_404(Recipe, id=obj.id)
        return UserShoppingRecipe.objects.filter(recipe=recipe,
                                                 user=user).exists()


class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'image', 'name', 'cooking_time')


class SubscriptionSerializer(serializers.ModelSerializer):
    recipes = ShortRecipeSerializer(source='author.recipes',
                                    many=True,
                                    read_only=True)
    email = serializers.CharField(source='author.email')
    id = serializers.IntegerField(source='author.id')
    username = serializers.CharField(source='author.username')
    first_name = serializers.CharField(source='author.first_name')
    last_name = serializers.CharField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes',
                  'recipes_count')

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.user).count()

    def get_is_subscribed(self, obj):
        return True
