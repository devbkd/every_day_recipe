# Generated by Django 4.2.4 on 2023-08-19 09:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_cart_recipes_alter_cart_user_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientinrecipe',
            old_name='recipe',
            new_name='recipes',
        ),
    ]
