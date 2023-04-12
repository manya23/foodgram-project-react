from abc import ABC

# from drf_extra_fields.fields import Base64ImageField
import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import Recipe, Tag, TagRecipe, Ingredient, IngredientRecipe, UserFavoriteRecipe


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

    # def to_representation(self, data):
    #     print('TagSerializer data: ', data.id)
    #     if not Tag.objects.filter(id=data.id):
    #         raise serializers.ValidationError({
    #             'detail': 'Страница не найдена.'
    #         })
    #
    #     return data


class IngredientRecipeInputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagRecipeSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source="tag.id")
    # name = serializers.CharField(source="tag.name")

    class Meta:
        model = TagRecipe
        fields = ('id',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    # tags = serializers.ListField()
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    ingredients = IngredientRecipeInputSerializer(many=True,
                                                  source='ingredientrecipe_set', )

    # image = Base64ImageField(
    #     max_length=None,
    #     use_url=True)
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ['tags', 'ingredients', 'name',
                  'text', 'cooking_time', 'image']
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        print('instance: ', instance)
        # ingredients = representation.pop('ingredients')
        # print('ingredients: \n', ingredients)
        # new_ingredients = list()
        # for ingredient in ingredients:
        #     # cur_ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
        #     # new_ingredients.append({'ingredient': cur_ingredient,
        #     #                         'amount': ingredient['amount']})
        #     ingredient_recipe = get_object_or_404(IngredientRecipe, ingredient=ingredient)
        #     new_ingredients.append({'id': ingredient_recipe,
        #                             'amount': ingredient['amount']})
        #
        # # representation['ingredients'] = instance.liked_by.count()
        # representation['ingredients'] = new_ingredients
        # print('representation: \n', representation)
        new_tags = list()
        for tag in representation['tags']:
            new_tags.append(get_object_or_404(Tag, id=tag))
        representation['tags'] = new_tags
        # TODO: почему в ответе поле с изображением пустое?
        # representation['image'] = instance.image
        return RecipeRetrieveSerializer(
            representation,
            context={'request': self.context.get('request')}
        ).data

    def create(self, validated_data):
        # print('validated_data: \n', validated_data)
        ingredients = validated_data.pop('ingredientrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            cur_ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            IngredientRecipe.objects.create(
                ingredient=cur_ingredient,
                recipe=recipe,
                amount=ingredient['amount']
            )
        # TODO: create TagRecipe record
        for tag in tags:
            print('tag: ', tag.id)
            cur_tag = get_object_or_404(Tag, id=tag.id)
            TagRecipe.objects.create(
                tag=cur_tag,
                recipe=recipe
            )
        return recipe

    # TODO: переписать метод
    # def update(self, instance, validated_data):
    #
    #     instance.name = validated_data.get('name', instance.name)
    #     instance.color = validated_data.get('color', instance.color)
    #     instance.birth_year = validated_data.get(
    #         'birth_year', instance.birth_year
    #         )
    #     instance.image = validated_data.get('image', instance.image)
    #     if 'achievements' in validated_data:
    #         achievements_data = validated_data.pop('achievements')
    #         lst = []
    #         for achievement in achievements_data:
    #             current_achievement, status = Achievement.objects.get_or_create(
    #                 **achievement
    #                 )
    #             lst.append(current_achievement)
    #         instance.achievements.set(lst)
    #
    #     instance.save()
    #     return instance


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
                  'text', 'cooking_time', 'image', )
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }
        depth = 2

    # def get_tags(self, obj):
    #     print('tag: ', obj.tags)
    #
    #     return obj.tags

    def get_is_favorited(self, obj):
        # TODO: make logic after setting Follow model
        recipe = get_object_or_404(Recipe, id=obj.id)
        print('recipe is: ', recipe)
        user = self.context['request'].user
        return UserFavoriteRecipe.objects.filter(recipe=recipe,
                                                 user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        # TODO: make logic after setting Follow model
        status = True
        return status


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }
