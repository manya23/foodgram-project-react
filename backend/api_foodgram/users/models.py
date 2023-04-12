from django.contrib.auth.models import AbstractUser, AbstractBaseUser, UserManager
from django.db import models


class User(AbstractUser):
    """Класс модели базы данных для хранения данных о пользователе"""

    REQUIRED_FIELDS = ['username', 'password']

    USERNAME_FIELD = 'email'
    USER: str = 'user'
    ADMIN: str = 'admin'

    CHOICES = (
        (USER, 'user'),
        (ADMIN, 'admin'),
    )

    objects = UserManager()

    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254
    )
    username = models.CharField(
        blank=False,
        verbose_name='Никнейм',
        max_length=150
    )
    first_name = models.CharField(
        blank=False,
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        blank=False,
        verbose_name='Фамилия',
        max_length=150
    )
    role = models.CharField(
        choices=CHOICES,
        default='user',
        max_length=128
    )
    password = models.CharField(
        blank=False,
        max_length=30
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'],
                                    name='unique_user')
        ]

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return self.role == self.ADMIN

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Класс модели базы данных для хранения подписок
    пользователей друг на друга."""

    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Издатель'
    )
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='publisher',
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow')
        ]

    def __str__(self):
        return f'Подписка {self.user} на {self.author}'
