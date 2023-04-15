# from drf_extra_fields.fields import Base64ImageField
import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers, validators

from users.serializers import CustomUserSerializer
from recipes.models import (Recipe, Tag, TagRecipe, Ingredient,
                            IngredientRecipe, UserFavoriteRecipe,
                            UserShoppingRecipe)


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


# No usage!!!
class TagRecipeSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source="tag.id")
    # name = serializers.CharField(source="tag.name")

    class Meta:
        model = TagRecipe
        fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
        lookup_field = 'name'
        extra_kwargs = {
            'url': {'lookup_field': 'name'}
        }


class IngredientRecipeInputSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient_id")
    amount = serializers.IntegerField()


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit')

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
            print(ingredient['ingredient_id'].id)
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
        print('recipe: ', recipe)
        return recipe

    # TODO: переписать метод
    def update(self, instance, validated_data):
        print('ok: ', instance.id)
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
                # cur_ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
                IngredientRecipe.objects.get_or_create(
                    ingredient=ingredient['ingredient_id'],
                    recipe=recipe,
                    amount=ingredient['amount']
                )
                print('cur_ingredient: ', ingredient['ingredient_id'])
                lst.append(ingredient['ingredient_id'])
            instance.ingredients.set(lst)
        print('validated_data: ', validated_data)
        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            lst = []
            print('tags_data: ', tags_data)
            for tag in tags_data:
                cur_tag = get_object_or_404(Tag, id=tag.id)
                TagRecipe.objects.get_or_create(
                    tag=cur_tag,
                    recipe=recipe
                )
                lst.append(cur_tag)
            instance.tags.set(lst)
        print('instance: ', instance.ingredients)
        instance.save()
        return instance

    # def validate_birth_year(self, value):
    #     year = dt.date.today().year
    #     if not (year - 40 < value <= year):
    #         raise serializers.ValidationError('Проверьте год рождения!')
    #     return value

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

    # def get_tags(self, obj):
    #     print('tag: ', obj.tags)
    #
    #     return obj.tags

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


# class ShortRecipeSerializer(serializers.ModelSerializer):
#     image = Base64ImageField(required=False, allow_null=True)
#
#     class Meta:
#         model = Recipe
#         fields = ('id', 'name', 'image', 'cooking_time', )
