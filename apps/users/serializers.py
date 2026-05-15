from rest_framework import serializers

from apps.users.models import TelegramProfile, User


class TelegramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProfile
        fields = [
            "telegram_id", "username", "first_name",
            "notifications_enabled", "last_active_at",
        ]
        read_only_fields = ["telegram_id", "last_active_at"]


class UserSerializer(serializers.ModelSerializer):
    telegram_profile = TelegramProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "is_active", "created_at", "telegram_profile"]
        read_only_fields = ["id", "is_active", "created_at"]


class TelegramRegisterSerializer(serializers.Serializer):
    """
    Used by the Telegram bot to register/update a user.
    """

    telegram_id = serializers.IntegerField(help_text="ID пользователя в Telegram")
    username = serializers.CharField(required=False, allow_blank=True, help_text="Имя пользователя (username)")
    first_name = serializers.CharField(required=False, allow_blank=True, help_text="Имя")
    last_name = serializers.CharField(required=False, allow_blank=True, help_text="Фамилия")
    language_code = serializers.CharField(required=False, allow_blank=True, help_text="Код языка пользователя")
