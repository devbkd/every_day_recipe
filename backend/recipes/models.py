from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    RegexValidator,
)
from django.db.models import (
    CASCADE,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    ImageField,
    ManyToManyField,
    Model,
    PositiveSmallIntegerField,
    TextField,
    UniqueConstraint,
)
from django.utils.translation import gettext_lazy as _

from users.models import User

MAX_LEN_NAME = 200
MAX_LEN_COLOR = 7
MAX_LEN_SLUG = 200

USER_RECIPE = 'Пользователь: {}> Рецепт: {}'
NAME_AUTHOR_TAG = 'Название: {}> Автор: {}> Тег: {}'
NAME_MEASUREMENT_UNIT = 'Название: {}> Единица измерения: {}'


class Tag(Model):
    """
    Модель для представления тегов с именем, цветом и идентификатором (slug).
    """

    name = CharField(
        max_length=MAX_LEN_NAME,
        unique=True,
        verbose_name='Тег',
        help_text='Тег',
    )
    color = CharField(
        max_length=MAX_LEN_COLOR,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Цвет должен быть в формате "#RRGGBB".',
                code='invalid_color',
            )
        ],
        verbose_name='Цвет',
        help_text='Цвет тега',
    )
    slug = CharField(
        max_length=MAX_LEN_SLUG,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_-]+$',
                message='Slug может содержать только латинские буквы, цифры, '
                'дефисы и подчеркивания.',
                code='invalid_slug',
            )
        ],
        verbose_name='Идентификатор',
        help_text='Идентифифкатор тега',
    )

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')

    def __str__(self):
        return f'{self.name}: {self.color}'


class Ingredient(Model):
    """
    Модель для представления ингредиентов, с единицой измерения.
    """

    name = CharField(
        max_length=MAX_LEN_NAME,
        verbose_name='Название',
        help_text='Название ингредиента',
    )
    measurement_unit = CharField(
        max_length=MAX_LEN_NAME,
        verbose_name='Единица измерения',
        help_text='Единица измерения ингредиента',
    )

    class Meta:
        verbose_name = _('Ингредиент')
        verbose_name_plural = _('Ингредиенты')

    def __str__(self):
        return NAME_MEASUREMENT_UNIT.format(self.name, self.measurement_unit)


class Recipe(Model):
    """
    Модель для представления рецептов, со связанными полями.
    """

    tags = ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег',
        help_text='Тег',
    )
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта',
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        verbose_name='Ингредиент',
        help_text='Ингредиент рецепта',
    )
    is_favorited = BooleanField(
        default=False,
        verbose_name='В избранном',
        help_text='Находится ли в избранном',
    )
    is_in_shopping_cart = BooleanField(
        default=False,
        verbose_name='В корзине',
        help_text='Находится ли в корзине',
    )
    name = CharField(
        max_length=MAX_LEN_NAME,
        verbose_name='Название',
        help_text='Название рецепта',
    )
    image = ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
        help_text='Ссылка на изображение на сайте',
    )
    text = TextField(
        verbose_name='Описание',
        help_text='Описание рецепта',
    )
    cooking_time = PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1, message='Время готовки должно быть больше 0.'
            ),
            MaxValueValidator(1440, message='Слишком большое время готовки.'),
        ],
        verbose_name='Время приготовления',
        help_text='Время приготовления (в минутах)',
    )
    pub_date = DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публиции',
        help_text='Дата публиции рецепта',
    )

    class Meta:
        verbose_name = _('Рецепт')
        verbose_name_plural = _('Рецепты')

    def __str__(self):
        return NAME_AUTHOR_TAG.format(self.name, self.author, self.tags)


class IngredientInRecipe(Model):
    """
    Модель вспомогательной тыблицы для ингредиентов в рецете.
    """

    recipes = ForeignKey(
        Recipe, on_delete=CASCADE, related_name='recipe_ingredients'
    )
    ingredient = ForeignKey(
        Ingredient, on_delete=CASCADE, related_name='recipe_ingredients'
    )
    amount = PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message='Количество должно быть больше 0.'),
            MaxValueValidator(1000, message='Слишком большое количество.'),
        ]
    )


class Favorite(Model):
    """
    Модель для представления избранных рецептов.
    """

    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='favorite_list',
        verbose_name='Пользователь',
        help_text='Пользователь',
    )
    recipes = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favorite_list',
        verbose_name='Рецепт',
        help_text='Избранный рецепт',
    )

    class Meta:
        verbose_name = _('Избранное')
        verbose_name_plural = _('Избранные')
        constraints = [
            UniqueConstraint(
                fields=(
                    'recipes',
                    'user',
                ),
                name='unique_favorites_for_recipes',
            ),
        ]

    def __str__(self):
        return USER_RECIPE.format(self.user, self.recipes)


class Cart(Model):
    """
    Модель для представления корзины рецептов.
    """

    recipes = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='cart_list',
        verbose_name='Рецепт',
        help_text='Рецепт',
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='cart_list',
        verbose_name='Пользователь',
        help_text='Пользователь',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=(
                    'recipes',
                    'user',
                ),
                name='unique_carts_for_recipes',
            ),
        ]
        verbose_name = _('Рецепт в корзине')
        verbose_name_plural = _('Рецепты в корзине')

    def __str__(self):
        return USER_RECIPE.format(self.user, self.recipes)
