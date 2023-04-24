"""
Using: python manage.py runscript load_ingredients
"""
from recipes.models import Ingredient
import os
import csv

CSV_PATH = (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            + '/data/ingredients.csv')


def run():
    with open(CSV_PATH) as file:
        reader = csv.reader(file)
        next(reader)

        Ingredient.objects.all().delete()

        for row in reader:
            film = Ingredient(name=row[0],
                              measurement_unit=row[1]
                              )
            film.save()
