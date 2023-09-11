from django.contrib.admin import ModelAdmin, register
from django.contrib.auth.admin import UserAdmin

from users.models import Subscription, User


@register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )
    list_filter = (
        'first_name',
        'email',
    )
    save_on_top = True


@register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user', 'author')
    list_filter = ('user', 'author')
    ordering = ('user',)
