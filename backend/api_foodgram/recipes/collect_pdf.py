from django.db.models import Sum
from django.template.loader import render_to_string
from recipes.models import IngredientRecipe


def collect_shopping_pdf(user):
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_recipes__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(Sum('amount')).order_by()

    return render_to_string(
        'pdf_template.html',
        {
            'username': user.username,
            'shopping_cart': ingredients
        }
    )
