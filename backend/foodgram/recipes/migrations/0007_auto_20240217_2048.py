# Generated by Django 3.2.6 on 2024-02-17 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0006_auto_20240217_1821'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shoppingcart_recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart_recipe', to='recipes.recipe')),
                ('shoppingcart_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('shoppingcart_user', 'shoppingcart_recipe'), name='unique_shoppingcart'),
        ),
    ]
