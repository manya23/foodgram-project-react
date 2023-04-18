import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators
from djoser.serializers import (UserSerializer,
                                UserCreateSerializer)

from recipes.models import (Recipe, Tag, TagRecipe, Ingredient,
                            IngredientRecipe, UserFavoriteRecipe,
                            UserShoppingRecipe)
from users.models import (User,
                          Follow)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CustomCreateUserSerializer (UserCreateSerializer):

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name',)

    def to_internal_value(self, data):
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        for field in [username, first_name, last_name,
                      email, password]:
            if not field:
                raise serializers.ValidationError({
                    f'{field}': 'Обязательное поле.'
                })

        return data


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
        else:
            return False

    def to_internal_value(self, data):
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        for field in [username, first_name, last_name,
                      email, password]:
            if not field:
                raise serializers.ValidationError({
                    f'{field}': 'Обязательное поле.'
                })

        return data


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
        # TODO: можно создать все сразу через один запрос: bulk_create
        for ingredient in ingredients:
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient_id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        for tag in tags:
            cur_tag = get_object_or_404(Tag, id=tag.id)
            TagRecipe.objects.create(
                tag=cur_tag,
                recipe=recipe
            )
        return recipe

    def update(self, instance, validated_data):
        recipe = get_object_or_404(Recipe, id=instance.id)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        if 'ingredientrecipe' in validated_data:
            ingredients_data = validated_data.pop('ingredientrecipe')
            lst = []
            for ingredient in ingredients_data:
                IngredientRecipe.objects.get_or_create(
                    ingredient=ingredient['ingredient_id'],
                    recipe=recipe,
                    amount=ingredient['amount']
                )
                lst.append(ingredient['ingredient_id'])
            instance.ingredients.set(lst)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            lst = []
            for tag in tags_data:
                cur_tag = get_object_or_404(Tag, id=tag.id)
                TagRecipe.objects.get_or_create(
                    tag=cur_tag,
                    recipe=recipe
                )
                lst.append(cur_tag)
            instance.tags.set(lst)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        new_tags = list()
        for tag in representation['tags']:
            new_tags.append(get_object_or_404(Tag, id=tag))
        representation['tags'] = new_tags
        # TODO: почему в ответе поле с изображением пустое?
        return RecipeRetrieveSerializer(
            representation,
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

    # def validate(self, data):
    #     print('data: ', data)
    #     return data
