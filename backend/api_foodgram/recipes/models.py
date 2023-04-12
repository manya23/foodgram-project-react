from django.db import models
from django.core.validators import MinValueValidator
# from djangoHexadecimal.fields import HexadecimalField

from users.models import User


class Ingredient(models.Model):
    """Класс модели базы данных для хранения доступных ингредиентов"""
    name = models.CharField(
        blank=False,
        verbose_name='Название ингредиента',
        max_length=200
    )
    measurement_unit = models.CharField(
        blank=False,
        verbose_name='Единицы измерения',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}/{self.measurement_unit}'


class Tag(models.Model):
    """Класс модели базы данных для тегов к рецептам"""

    CHOICES = (
        ('#eb4034', 'красный'),
        ('#ebe234', 'желтый'),
        ('#34eb37', 'зеленый'),
        ('#4634eb', 'синий'),
    )

    name = models.CharField(
        blank=False,
        unique=True,
        verbose_name='Название тега',
        max_length=200
    )
    color = models.CharField(
        choices=CHOICES,
        default='user',
        blank=False,
        verbose_name='Цвет в HEX',
        max_length=7
    )
    slug = models.SlugField(
        blank=False,
        unique=True,
        verbose_name='Название тега: slug',
        max_length=200
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Класс модели базы данных для хранения рецептов"""
    name = models.CharField(
        blank=False,
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
    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1), ]
    )
    text = models.TextField(
        blank=False,
        verbose_name='Описание рецепта',
        help_text='Введите описание рецепта',
    )
    # TODO: выбор из предустановленного списка, с указанием количества и единицы измерения
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through='IngredientRecipe'
    )
    # TODO: можно установить несколько тегов на один рецепт, выбор из предустановленных
    tags = models.ManyToManyField(
        Tag,
        blank=False,
        through='TagRecipe'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=False
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


class UserFavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписчик'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Избранный рецепт'
    )

    def __str__(self):
        return f'Пользователю {self.user} нравится {self.recipe}'


class UserShoppingRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shipper',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipes',
        verbose_name='Список покупок'
    )

    def __str__(self):
        return f'{self.recipe} в корзине пользователя {self.user}'
