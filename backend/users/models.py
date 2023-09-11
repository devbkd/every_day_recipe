from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    CharField,
    CheckConstraint,
    EmailField,
    F,
    ForeignKey,
    Model,
    Q,
    UniqueConstraint,
)
from django.utils.translation import gettext_lazy as _

from .validators import validate_username

MAX_LEN_EMAIL = 254
MAX_LEN_USERS = 150
MIN_LEN_USERNAME = 3
MAX_LEN_PASSWORD = 128
FOLLOW = '{} подписан(а) на {}'


class User(AbstractUser):
    email = EmailField(
        max_length=MAX_LEN_EMAIL,
        unique=True,
        verbose_name='Адрес электронной почты',
        help_text='*Email',
    )
    username = CharField(
        max_length=MAX_LEN_USERS,
        unique=True,
        verbose_name='Уникальное имя пользователя',
        help_text='Уникальное имя пользователя',
        validators=[validate_username],
    )
    first_name = CharField(
        max_length=MAX_LEN_USERS,
        verbose_name='Имя',
        help_text='Имя пользователя',
    )
    last_name = CharField(
        max_length=MAX_LEN_USERS,
        verbose_name="Фамилия",
        help_text='Фамилия пользователя',
    )
    password = CharField(
        max_length=MAX_LEN_PASSWORD,
        verbose_name='Пароль',
        help_text='Пароль',
    )

    class Meta:
        verbose_name = _('Пользователя')
        verbose_name_plural = _('Пользователи')
        ordering = ('username',)

    def __str__(self) -> str:
        return f'{self.username}: {self.email}'


class Subscription(Model):
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='author',
        verbose_name='Автор',
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            UniqueConstraint(name='unique_follow', fields=['author', 'user']),
            CheckConstraint(name='not_follow', check=~Q(user=F('author'))),
        ]

    def __str__(self):
        return FOLLOW.format(self.user.username, self.author.username)
