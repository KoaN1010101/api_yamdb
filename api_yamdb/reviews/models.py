import datetime

from api.validators import username_validator
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def current_year():
    return datetime.date.today().year


class User(AbstractUser):
    ROLE_USER = 'user'
    ROLE_MODERATOR = 'moderator'
    ROLE_ADMIN = 'admin'
    ROLES = [(ROLE_USER, 'Пользователь'),
             (ROLE_MODERATOR, 'Модератор'),
             (ROLE_ADMIN, 'Администратор'),
             ]
    username = models.CharField(
        'Имя пользователя',
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
        validators=[username_validator]
    )
    email = models.EmailField(
        'Почта',
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=settings.FIRST_NAME_MAX_LENGTH,
        blank=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=settings.LAST_NAME_MAX_LENGTH,
        blank=True
    )
    bio = models.TextField('Биография', null=True, blank=True)
    role = models.CharField(
        'Роль',
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=ROLE_USER,
        blank=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    @property
    def is_admin(self):
        return self.is_staff or self.role == User.ROLE_ADMIN

    @property
    def is_moderator(self):
        return self.role == User.ROLE_MODERATOR


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название категории")
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']


class Title(models.Model):
    name = models.CharField(max_length=256,
                            verbose_name="Название произведения")
    year = models.PositiveSmallIntegerField(
        default=current_year, validators=[
            MinValueValidator(settings.MIN_VALUE_VALIDATOR)], db_index=True
    )
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, related_name="titles", null=True
    )
    genre = models.ManyToManyField(Genre, related_name="titles")

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Review(models.Model):

    title = models.ForeignKey(Title, on_delete=models.CASCADE,
                              related_name="reviews")
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="reviews")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True,
                                    db_index=True)
    score = models.PositiveSmallIntegerField(
        "Оценка",
        default=0,
        validators=[
            MinValueValidator(
                settings.MIN_VALUE_VALIDATOR,
                message="Минимальная оценка - 1"),
            MaxValueValidator(settings.MAX_VALUE_VALIDATOR,
                              message="Максимальная оценка - 10"),
        ],
    )

    class Meta:
        verbose_name = "Отзыв"
        ordering = ["-pub_date"]
        constraints = (
            models.UniqueConstraint(
                fields=["author", "title"], name="unique_relationships"
            ),
        )

    def __str__(self):
        return self.text[:settings.TEXT_PARAM]


class Comment(models.Model):

    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField(verbose_name="Текст")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации комментария"
    )

    class Meta:
        verbose_name = "Комментарий"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:settings.TEXT_PARAM]
