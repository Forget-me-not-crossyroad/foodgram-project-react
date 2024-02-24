from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.deconstruct import deconstructible
from users.models import User


@deconstructible
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
    slug = models.SlugField(unique=True, max_length=200)
    name = models.CharField(unique=True, max_length=200)
    color = models.CharField(
        default=BLACK, unique=True, max_length=7, choices=COLOR_LIST
    )

    @classmethod
    def get_default_tag(cls):
        obj, created = cls.objects.get_or_create(
            name='Полдник',
            slug='afternoon_tea',
        )
        return obj

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(unique=True, max_length=150)
    measurement_unit = models.CharField(max_length=150)

    @classmethod
    def get_default_pk(cls):
        obj, created = cls.objects.get_or_create(
            name='сахар', measurement_unit='г'
        )
        return obj.pk

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=150, default='Укажите название рецепта')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    text = models.TextField(default='Дополните рецепт описанием')
    image = models.ImageField(
        null=True,
        default=None,
        upload_to='media/',
    )
    created = models.DateTimeField(auto_now_add=True)
    cooking_time = models.IntegerField(
        default=5,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(1000)],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        default=Ingredient.get_default_pk(),
    )
    tags = models.ManyToManyField(Tag, default=Tag.get_default_tag())

    def __str__(self):
        return self.name


@deconstructible
class IngredientAmountRecipe(models.Model):
    amount = models.CharField(max_length=150, default=1)

    @classmethod
    def get_default_amount(cls):
        obj, created = cls.objects.get_or_create(amount=1)
        return obj

    def __str__(self):
        return self.amount


class IngredientRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        related_name='RecipeIngredients',
        on_delete=models.CASCADE,
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='RecipeIngredients',
    )
    amount = models.ForeignKey(
        'IngredientAmountRecipe',
        on_delete=models.CASCADE,
        related_name='RecipeIngredients',
    )


class Favorite(models.Model):
    favorited_user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='favorited_user'
    )
    favorited_recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='favorited_recipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['favorited_user', 'favorited_recipe'],
                name='unique_favorited',
            ),
        ]


class ShoppingCart(models.Model):
    shoppingcart_user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='shoppingcart_user',
    )
    shoppingcart_recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE, related_name='shoppingcart_recipe'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['shoppingcart_user', 'shoppingcart_recipe'],
                name='unique_shoppingcart',
            ),
        ]
