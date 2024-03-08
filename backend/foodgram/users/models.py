from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import BadRequest
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        email = email.lower()

        user = self.model(email=email, **kwargs)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email, password=password, **kwargs)

        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    USER = 'user'
    ADMIN = 'admin'
    ROLE_USER = [(USER, 'Пользователь'), (ADMIN, 'Администратор')]
    role = models.CharField(max_length=15, choices=ROLE_USER, default=USER)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    password = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    email = models.EmailField(unique=True, max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password', 'first_name', 'last_name']

    def set_new_password(self, current_password, new_password):
        if self.check_password(current_password):
            self.set_password(new_password)
            self.save()
        else:
            raise BadRequest('inserted_old_password_doesnt_match_old_password')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email


class Me(User):
    # практика использования proxy-моделей
    # взята из коммерческого опыта и для
    # удобочитаемости кода для отдельного
    # энпоинта

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        pass

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователя'
        proxy = True


class SetPassword(models.Model):
    # при попытке переопределить функционал на
    # дефолтный set_password из djoser
    # возникли большие проблемы с переопределением роутов,
    # поэтому оставил кастомный функционал
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    current_password = models.CharField(max_length=150)
    new_password = models.CharField(max_length=150)

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.user.set_new_password(self.current_password, self.new_password)

    class Meta:
        verbose_name = 'Модель для изменения пароля'
        verbose_name_plural = 'Модели для изменения пароля'


class Subscription(models.Model):
    subscribed_to = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='subscribed_to'
    )
    subscriber = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='subscriber'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscribed_to', 'subscriber'],
                name='unique_subscription',
            ),
            models.CheckConstraint(
                check=~models.Q(subscribed_to=models.F('subscriber')),
                name='check_self_subscription',
            ),
        ]

