from django.db import models

from users.models import User


class Recipe(models.Model):
    name = models.CharField(max_length=150)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
