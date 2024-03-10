# Generated by Django 3.2.6 on 2024-03-10 23:02

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0008_alter_tag_color'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={'verbose_name': 'Избранный рецепт', 'verbose_name_plural': 'Избранные рецепты'},
        ),
        migrations.AlterModelOptions(
            name='ingredient',
            options={'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
        migrations.AlterModelOptions(
            name='ingredientamountrecipe',
            options={'verbose_name': 'Модель для хранения amount', 'verbose_name_plural': 'Модели для хранения amount'},
        ),
        migrations.AlterModelOptions(
            name='ingredientrecipe',
            options={'verbose_name': 'Промежуточная модель ingredient-recipe', 'verbose_name_plural': 'Промежуточные модели ingredient-recipe'},
        ),
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-id'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'verbose_name': 'Список покупок', 'verbose_name_plural': 'Списки покупок'},
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Тэг', 'verbose_name_plural': 'Тэги'},
        ),
        migrations.AlterField(
            model_name='favorite',
            name='favorited_recipe',
            field=models.ForeignKey(help_text='Избранный рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='favorited_recipe', to='recipes.recipe', verbose_name='Лайкнутый рецепт'),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='favorited_user',
            field=models.ForeignKey(help_text='В избранном у пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='favorited_user', to=settings.AUTH_USER_MODEL, verbose_name='Лайкнувший пользователь'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Название единицу измерения, не более 200 символов', max_length=150, verbose_name='Единица измерения'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Название ингредиента, не более 200 символов', max_length=150, unique=True, verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientamountrecipe',
            name='amount',
            field=models.CharField(default=1, help_text='Введите количество', max_length=150, validators=[django.core.validators.MinValueValidator(2, 'Минимальное количество ингредиента - 2')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.ForeignKey(help_text='Добавьте количество ингредиента', on_delete=django.db.models.deletion.CASCADE, related_name='RecipeIngredients', to='recipes.ingredientamountrecipe', verbose_name='Количество ингредиента'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='ingredient',
            field=models.ForeignKey(help_text='Добавьте ингредиенты', on_delete=django.db.models.deletion.CASCADE, related_name='RecipeIngredients', to='recipes.ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='recipe',
            field=models.ForeignKey(help_text='Выбрать рецепт', on_delete=django.db.models.deletion.CASCADE, related_name='RecipeIngredients', to='recipes.recipe', verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(help_text='Поле связи с моделью автора', on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.IntegerField(blank=True, default=5, help_text='Время приготовления блюда в минутах', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1000)], verbose_name='Время приготовления'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='Создается автоматически при создании блюда', verbose_name='Время создания'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, help_text='Загрузить изображение блюда', null=True, upload_to='media/', verbose_name='Изображение блюда'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(default=4, help_text='Поле связи с моделью ингредиента', through='recipes.IngredientRecipe', to='recipes.Ingredient', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(default='Укажите название рецепта', help_text='Название рецепта, не более 200 символов', max_length=150, verbose_name='Название рецепта'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(default=recipes.models.Tag(4, 'afternoon_tea', 'Полдник', '000000'), help_text='Укажите тег', to='recipes.Tag', verbose_name='Поле связи с моделью тега'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(default='Дополните рецепт описанием', help_text='Введите описание приготовления', verbose_name='Текст описания'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='shoppingcart_recipe',
            field=models.ForeignKey(help_text='Рецепт в корзине', on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart_recipe', to='recipes.recipe', verbose_name='Добавивлено в корзину'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='shoppingcart_user',
            field=models.ForeignKey(help_text='В корзине у пользователя', on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcart_user', to=settings.AUTH_USER_MODEL, verbose_name='Добавивший в корзину'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(choices=[('e26e24', 'оранжевый'), ('4ab54f', 'зеленый'), ('8574d4', 'фиолетовый'), ('000000', 'черный')], default='000000', help_text='Поле выбора цвета', max_length=7, unique=True, verbose_name='Цвет HEX, дефолтный - BLACK'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(help_text='Введите текст', max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(help_text='Идентификатор страницы для URL; разрешены символы латиницы, цифры, дефис и подчёркивание.', max_length=200, unique=True, verbose_name='Идентификатор'),
        ),
        migrations.AddConstraint(
            model_name='ingredientrecipe',
            constraint=models.UniqueConstraint(fields=('recipe', 'ingredient'), name='unique_recipe_ingredients'),
        ),
        migrations.AddConstraint(
            model_name='recipe',
            constraint=models.UniqueConstraint(fields=('author', 'name'), name='unique_recipe'),
        ),
    ]
