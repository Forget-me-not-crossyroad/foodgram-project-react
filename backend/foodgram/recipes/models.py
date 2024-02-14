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
    ]
    slug = models.SlugField(unique=True, max_length=200)
    name = models.CharField(unique=True, max_length=200)
    color = models.CharField(default=BLACK, unique=True, max_length=7, choices=COLOR_LIST)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(unique=True, max_length=150)
    measurement_unit = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')

    def __str__(self):
        return self.name