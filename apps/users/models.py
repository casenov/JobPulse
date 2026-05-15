from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from core.mixins import TimestampedModel


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, TimestampedModel):
    """
    Custom user model.
    Primary auth method: Telegram.
    Optional: email/password for web clients.
    """

    email = models.EmailField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email or f"User #{self.pk}"


class TelegramProfile(TimestampedModel):
    """
    Telegram identity linked to a User.
    Separate model for clean separation of concerns.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="telegram_profile"
    )
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)
    last_active_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Профиль Telegram"
        verbose_name_plural = "Профили Telegram"

    def __str__(self):
        return f"@{self.username or self.telegram_id}"
