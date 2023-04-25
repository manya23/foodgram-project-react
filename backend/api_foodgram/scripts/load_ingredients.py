"""
Using: python manage.py runscript load_ingredients
"""
import csv
import os

from recipes.models import Ingredient

CSV_PATH = (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            + '/data/ingredients.csv')


def run():
    with open(CSV_PATH) as file:
        reader = csv.reader(file)
        next(reader)

        # get_or_create()
        # Ingredient.objects.all().delete()

        for row in reader:
            Ingredient.objects.get_or_create(
                name=row[0],
                measurement_unit=row[1]
            )
            # film = Ingredient(name=row[0],
            #                   measurement_unit=row[1]
            #                   )
            # film.save()
