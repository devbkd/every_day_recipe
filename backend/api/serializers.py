from django.db.transaction import atomic
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import (
    IntegerField,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ReadOnlyField,
    SerializerMethodField,
    ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)
from users.models import Subscription, User


class UserSerializer(ModelSerializer):
    """Сериализатор для использования с моделью User."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj: User):
        user = self.context.get('request').user
        if user.is_anonymous or (user == obj):
            return False

        return user.follower.filter(author=obj).exists()

    def create(self, validated_data: dict):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserCreateSerializer(DjoserUserCreateSerializer):
    """Сериализатор создания пользователя с определенными полями."""

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class SubscribeSerializer(ModelSerializer):
    """Сериализатор вывода авторов на которых подписан текущий пользователь."""

    id = ReadOnlyField(source='author.id')
    username = ReadOnlyField(source='author.username')
    first_name = ReadOnlyField(source='author.first_name')
    last_name = ReadOnlyField(source='author.last_name')
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'recipes',
            'is_subscribed',
            'recipes_count',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscriptions'),
                message='Подписка уже существует',
            )
        ]

    def validate(self, data):
        user = self.context['request'].user
        author = data['author']
        if user == author:
            raise ValidationError('Невозможно подписаться на самого себя')
        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого автора.')
        return data

    def get_is_subscribed(self, obj):
        request = self.context.get('request').user
        if request.is_authenticated:
            return Subscription.objects.filter(
                user=request, author=obj.id
            ).exists()
        return False

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit'
        )
        if recipes_limit:
            queryset = obj.author.recipes.all()[: int(recipes_limit)]
        else:
            queryset = obj.author.recipes.all()
        return RecipeForListSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()


class TagSerializer(ModelSerializer):
    """Сериализатор тега с указанными полями и только для чтения."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """
    Сериализатор ингредиента с указанными полями и валидатором уникальности.
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'unit'),
                message='Такой ингредиент уже есть.',
            )
        ]


class ReadIngredientSerializer(ModelSerializer):
    """
    Сериализатор чтения ингредиента с определенными полями
    и связанным первичным ключом.
    """

    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class IngredientInRecipeSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeForListSerializer(ModelSerializer):
    """
    Сериализатор ингредиента в рецепте с определенными полями
    и только для чтения.
    """

    image = SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class ReadRecipeSerializer(ModelSerializer):
    """
    Сериализатор чтения рецепта с указанными полями
    и дополнительными вычисляемыми полями.
    """

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True, read_only=True, source='recipe_ingredients'
    )
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )
        read_only_fields = (
            'is_favorited',
            'is_in_shopping_cart',
            'author',
            'tags',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.favorite_list.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return obj.cart_list.filter(user=request.user).exists()
        return False


class CreatRecipeSerializer(ModelSerializer):
    """
    Сериализатор создания рецепта с указанными полями
    и методами для валидации и создания.
    """

    tags = PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    ingredients = ReadIngredientSerializer(many=True)
    image = Base64ImageField()
    cooking_time = IntegerField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'author',
            'image',
            'text',
            'ingredients',
            'tags',
            'cooking_time',
        )

    def validate(self, data):
        tags = self.initial_data.get('tags')
        ingredients = self.initial_data.get('ingredients')

        if not ingredients:
            raise ValidationError('Нужно выбрать ингердиенты.')
        if not tags:
            raise ValidationError('Нужно выбрать хотя бы один тег.')

        data.update(
            {
                'tags': tags,
                'ingredients': ingredients,
                'author': self.context.get('request').user,
            }
        )
        return data

    @staticmethod
    def create_ingredients(ingredients, recipes):
        ingredient_list = []
        for ingredient in ingredients:
            ingredient_list.append(
                IngredientInRecipe(
                    ingredient_id=ingredient['id'],
                    recipes=recipes,
                    amount=ingredient['amount'],
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredient_list)

    @atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        self.create_ingredients(ingredients, recipes)
        return recipes

    @atomic
    def update(self, instance, validated_data):
        instance.ingredients.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ReadRecipeSerializer(
            instance, context={'request': self.context.get('request')}
        ).data


class ReadCartSerializer(ModelSerializer):
    """
    Сериализатор чтения корзины с указанными полями
    и методом для преобразования данных.
    """

    class Meta:
        model = Cart
        fields = ('recipes', 'user')
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipes'),
                message='Рецепт уже в корзине.',
            )
        ]

    def to_representation(self, instance):
        return RecipeForListSerializer(
            instance.recipes, context={'request': self.context.get('request')}
        ).data


class ReadFavoriteSerializer(ModelSerializer):
    """Сериализатор для чтения избранных рецептов
    с данными пользователя и рецептов.
    """

    class Meta:
        model = Favorite
        fields = ('user', 'recipes')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipes'),
                message='Рецепт уже добавлен в избранные.',
            )
        ]

    def to_representation(self, instance):
        return RecipeForListSerializer(
            instance.recipes, context={'request': self.context.get('request')}
        ).data
