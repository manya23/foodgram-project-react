from django.db.models import Sum

from api_foodgram.settings import MEDIA_ROOT, STATIC_ROOT
from recipes.models import IngredientRecipe


def collect_shopping_pdf(user):
    ingredients = IngredientRecipe.objects.filter(
        recipe__shopping_recipes__user=user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit'
    ).annotate(Sum('amount')).order_by()
    report_lines = list()
    ingredient_data = str()
    temp_lines = read_template_report(
        f'{STATIC_ROOT}/pdf_template.html'
    )
    for ingredient in ingredients:
        ingredient_data += (
            "<li>"
            f"{ingredient['ingredient__name']}: "
            f"{ingredient['amount__sum']}"
            f"{ingredient['ingredient__measurement_unit']}"
            "</li>"

        )
    for line in temp_lines:
        line = line.replace('$$$Имя пользователя$$$', str(user.username))
        line = line.replace('$$$Список покупок$$$', str(ingredient_data))
        report_lines.append(line)
    report_part_name = f'/shopping_list_for_{user.username}'
    report_name = '{folder_name}{name}'.format(
        folder_name=MEDIA_ROOT,
        name=report_part_name
    )
    save_report(report_name, report_lines)
    return report_name


def read_template_report(path):
    with open(path) as f:
        lines = f.readlines()
    return lines


def save_report(name, report_lines):
    path = name + '.html'
    with open(path, 'w') as f:
        for line in report_lines:
            f.write("%s\n" % line)