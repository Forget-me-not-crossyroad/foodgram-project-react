from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    BLACK = '000000'
    ORANGE = 'e26e24'
    GREEN = '4ab54f'
    PURPLE = '8574d4'
    COLOR_LIST = [
        (ORANGE, 'оранжевый'),
        (GREEN, 'зеленый'),
        (PURPLE, 'фиолетовый'),
        (BLACK, 'черный'),
    ]
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы'
            ' латиницы, цифры, дефис и подчёркивание.'
        ),
    )
    name = models.CharField(
        unique=True,
        max_length=200,
        help_text='Введите текст',
    )
    color = models.CharField(
        default=BLACK,
        unique=True,
        max_length=7,
        choices=COLOR_LIST,
        verbose_name='Цвет HEX, дефолтный - BLACK',
        help_text='Поле выбора цвета',
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Ингредиент',
        help_text='Название ингредиента, не более 200 символов',
    )
    measurement_unit = models.CharField(
        max_length=150,
        verbose_name='Единица измерения',
        help_text='Название единицу измерения, не более 200 символов',
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='Название рецепта',
        help_text='Название рецепта, не более 200 символов',
        max_length=150,
        default='Укажите название рецепта',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        help_text='Поле связи с моделью автора',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    text = models.TextField(
        verbose_name='Текст описания',
        help_text='Введите описание приготовления',
        default='Дополните рецепт описанием',
    )
    image = models.ImageField(
        verbose_name='Изображение блюда',
        help_text='Загрузить изображение блюда',
        null=True,
        default=None,
        upload_to='media/',
    )
    created = models.DateTimeField(
        verbose_name='Время создания',
        help_text='Создается автоматически при создании блюда',
        auto_now_add=True,
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        help_text='Время приготовления блюда в минутах',
        default=5,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиент',
        help_text='Поле связи с моделью ингредиента',
        through='IngredientRecipe',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Поле связи с моделью тега',
        help_text='Укажите тег',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'name'], name='unique_recipe'
            )
        ]

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        help_text='Добавьте ингредиенты',
        related_name='RecipeIngredients',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Название рецепта',
        help_text='Выбрать рецепт',
        on_delete=models.CASCADE,
        related_name='RecipeIngredients',
    )
    amount = models.CharField(
        verbose_name='Количество ингредиента',
        help_text='Добавьте количество ингредиента',
        max_length=150,
        default=1,
    )

    class Meta:
        verbose_name = 'Промежуточная модель ingredient-recipe'
        verbose_name_plural = 'Промежуточные модели ingredient-recipe'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredients',
            )
        ]


class Favorite(models.Model):
    favorited_user = models.ForeignKey(
        'users.User',
        verbose_name='Лайкнувший пользователь',
        help_text='В избранном у пользователя',
        on_delete=models.CASCADE,
        related_name='favorited_user',
    )
    favorited_recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Лайкнутый рецепт',
        help_text='Избранный рецепт',
        on_delete=models.CASCADE,
        related_name='favorited_recipe',
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['favorited_user', 'favorited_recipe'],
                name='unique_favorited',
            ),
        ]


class ShoppingCart(models.Model):
    shoppingcart_user = models.ForeignKey(
        'users.User',
        verbose_name='Добавивший в корзину',
        help_text='В корзине у пользователя',
        on_delete=models.CASCADE,
        related_name='shoppingcart_user',
    )
    shoppingcart_recipe = models.ForeignKey(
        'Recipe',
        verbose_name='Добавивлено в корзину',
        help_text='Рецепт в корзине',
        on_delete=models.CASCADE,
        related_name='shoppingcart_recipe',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['shoppingcart_user', 'shoppingcart_recipe'],
                name='unique_shoppingcart',
            ),
        ]
