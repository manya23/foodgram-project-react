from django.shortcuts import get_object_or_404
from recipes.models import IngredientRecipe, Recipe, Tag, TagRecipe
from rest_framework import status
from rest_framework.response import Response


def create_recipe_record(
        ingredients,
        recipe,
        tags
):
    ingredients_bulk = list()
    for ingredient in ingredients:
        ingredients_bulk.append(
            IngredientRecipe(
                ingredient=ingredient['ingredient_id'],
                recipe=recipe,
                amount=ingredient['amount']
            )
        )
    IngredientRecipe.objects.bulk_create(
        ingredients_bulk,
        batch_size=15,
        ignore_conflicts=True

    )
    tags_bulk = list()
    for tag in tags:
        cur_tag = get_object_or_404(Tag, id=tag.id)
        tags_bulk.append(
            TagRecipe(
                tag=cur_tag,
                recipe=recipe
            )
        )
    TagRecipe.objects.bulk_create(
        tags_bulk,
        batch_size=15,
        ignore_conflicts=True
    )


def add_or_delete_user_recipe_connection(
        serializer,
        viewset_object,
        connection_model,
        request,
        pk
):
    user = viewset_object.request.user
    recipe = get_object_or_404(Recipe, id=pk)
    if viewset_object.request.method == 'POST':
        # добавление рецепта в список
        connection_model.objects.get_or_create(
            user=user,
            recipe=recipe
        )
        serializer = serializer(
            recipe,
            context={'request': request}
        )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    # удаление рецепта из списка
    connection_model.objects.filter(
        recipe=recipe,
        user=user
    ).delete()
    return Response(status=status.HTTP_200_OK)
