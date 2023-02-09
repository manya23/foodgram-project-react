from django.db import models
# from djangoHexadecimal.fields import HexadecimalField

from apps.users.models import User


class Ingredient(models.Model):
    """Класс модели базы данных для хранения доступных ингредиентов"""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения',
        max_length=200
    )

    def __str__(self):
        return f'{self.name}/{self.measurement_unit}'


class Tag(models.Model):
    """Класс модели базы данных для тегов к рецептам"""
    name = models.CharField(
        verbose_name='Название тега',
        max_length=200
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=7
    )
    slug = models.SlugField(
        verbose_name='Название тега',
        unique=True,
        max_length=200
    )


class Recipe(models.Model):
    """Класс модели базы данных для хранения рецептов"""
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата пубикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    cooking_time = models.IntegerField()
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')
    tags = models.ManyToManyField(Tag, through='TagRecipe')
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:15]


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.IntegerField()

    def __str__(self):
        return f'{self.ingredient} from {self.recipe}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.tag} {self.recipe}'
