from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.mixins import CustomMixin
from api.serializers import (
    CreatRecipeSerializer,
    IngredientSerializer,
    ReadCartSerializer,
    ReadFavoriteSerializer,
    ReadRecipeSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)
from users.models import Subscription, User
from utils.filters import IngredientFilter, RecipeFilter
from utils.paginators import PageLimitPagination
from utils.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly


class UserViewSet(UserViewSet):
    """Вьюсет для работы с пользователями."""

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()

    @action(detail=False, permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        """Метод для возвращения подпискок пользователя."""
        user = request.user
        subscriptions = user.follower.all()
        paginator = PageLimitPagination()
        result_page = paginator.paginate_queryset(subscriptions, request)
        serializer = SubscribeSerializer(
            result_page, many=True, context={'request': request}
        )
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id=None):
        """Метод для создания/удаления подписки на автора."""
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if Subscription.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription = Subscription.objects.create(
                user=request.user, author=author
            )
            serializer = SubscribeSerializer(
                subscription, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not Subscription.objects.filter(
                user=request.user, author=author
            ).exists():
                return Response(
                    {'errors': 'Подписка не существует.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Subscription.objects.filter(
                user=request.user, author=author
            ).delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )


class TagViewSet(CustomMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class IngredientViewSet(CustomMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [
        IsAuthorOrReadOnly,
    ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return CreatRecipeSerializer
        return ReadRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def _common_post(self, request, pk, serializer_class):
        recipes = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': request.user.id,
            'recipes': recipes.id,
        }
        serializer = serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=('POST',))
    def favorite(self, request, pk):
        return self._common_post(request, pk, ReadFavoriteSerializer)

    @favorite.mapping.delete
    def destroy_favorite(self, request, pk):
        favorite_list = get_object_or_404(
            Favorite,
            user=request.user,
            recipes=get_object_or_404(Recipe, id=pk),
        )
        favorite_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('POST',))
    def shopping_cart(self, request, pk):
        return self._common_post(request, pk, ReadCartSerializer)

    @shopping_cart.mapping.delete
    def destroy_shopping_cart(self, request, pk):
        cart_list = get_object_or_404(Cart, user=request.user, recipes__id=pk)
        cart_list.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=('GET',))
    def download_shopping_cart(self, request):
        text = 'Список покупок:'
        user = request.user
        filename = f'{user.username}_shopping_list.txt'
        ingredients = (
            IngredientInRecipe.objects.filter(recipes__cart_list__user=user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(amount=Sum('amount'))
        )
        text += '\n'.join(
            [
                f'{ingredient.get("ingredient__name")}: '
                f'{ingredient.get("amount")} '
                f'{ingredient.get("ingredient__measurement_unit")}'
                for ingredient in ingredients
            ]
        )
        response = HttpResponse(text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
