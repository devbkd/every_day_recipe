from django.contrib.admin import ModelAdmin, TabularInline, register

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    Tag,
)


@register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'color', 'slug')
    list_filter = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    save_on_top = True


class RecipeInIngredientAdmin(TabularInline):
    model = IngredientInRecipe


@register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = (
        'name',
        'author',
        'is_favorited',
        'is_in_shopping_cart',
        'image',
        'text',
        'cooking_time',
        'pub_date',
    )
    list_filter = ('name', 'author__username', 'tags__name')
    search_fields = ('name', 'author__username', 'tags__name')
    inlines = (RecipeInIngredientAdmin,)
    save_on_top = True


@register(Favorite)
class FavoriteAdmin(ModelAdmin):
    list_display = ('user', 'recipes')
    list_filter = ('recipes__tags',)
    search_fields = ('recipes__name', 'user__username')


@register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('user', 'recipes')
    list_filter = ('recipes__tags',)
    search_fields = ('recipes__name', 'user__username')
