from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validations import validate_username, validate_year


class BaseDescription(models.Model):
    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME_DESCRIPTION,
        unique=True
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('-name',)


class Category(BaseDescription):

    class Meta(BaseDescription.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(BaseDescription):

    class Meta(BaseDescription.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    DISPLAY = (
        '{name}, '
        '{year}'
    )

    name = models.TextField(
        db_index=True,
        verbose_name='Произведение'
    )

    year = models.PositiveSmallIntegerField(
        db_index=True,
        null=True,
        validators=[validate_year]
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='titles',
        verbose_name='Жанр'
    )

    def __str__(self):
        return self.DISPLAY.format(
            name=self.name,
            year=self.year
        )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
        (USER, 'Пользователь'),
    ]

    username = models.CharField(
        verbose_name='Пользователь',
        max_length=settings.MAX_LENGTH_USERNAME,
        unique=True,
        validators=[validate_username]
    )
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=settings.MAX_LENGTH_EMAIL,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    role = models.TextField(
        verbose_name='Роль',
        max_length=max(len(role) for role, _ in ROLES),
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='Биография',
        null=True,
        blank=True
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=settings.MAX_LENGTH_CONFIRMATION_CODE,
        null=True,
        default=settings.DEFAULT_CONFIRMATION_CODE
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    @property
    def is_admin(self):
        return (self.role == self.ADMIN or self.is_staff)

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        return self.role == self.USER

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )


class BaseFeedBack(models.Model):
    STR_TEMPLATE = '{username}: {text:10} ... {pub_date}'

    text = models.TextField(
        verbose_name='Отзыв',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.STR_TEMPLATE.format(
            username=self.author.username,
            text=self.text,
            pub_date=self.pub_date,
        )

    class Meta:
        abstract = True
        ordering = ['-pub_date']


class Review(BaseFeedBack):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    score = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )

    class Meta(BaseFeedBack.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comments(BaseFeedBack):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE
    )

    class Meta(BaseFeedBack.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
