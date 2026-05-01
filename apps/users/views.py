from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import TelegramProfile, User
from apps.users.serializers import (
    TelegramRegisterSerializer,
    UserSerializer,
)


class MeView(generics.RetrieveAPIView):
    """GET /api/v1/users/me/ — current user profile."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class TelegramRegisterView(APIView):
    """
    POST /api/v1/users/telegram/register/
    Called by the Telegram bot when user sends /start.
    Creates or updates the user + TelegramProfile.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TelegramRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile, created = TelegramProfile.objects.update_or_create(
            telegram_id=data["telegram_id"],
            defaults={
                "username": data.get("username", ""),
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "language_code": data.get("language_code", ""),
                "last_active_at": timezone.now(),
            },
        )

        if created:
            user = User.objects.create_user()
            profile.user = user
            profile.save(update_fields=["user"])
        else:
            user = profile.user

        user_data = UserSerializer(user).data
        return Response(
            {"user": user_data, "created": created},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class TelegramToggleNotificationsView(APIView):
    """
    POST /api/v1/users/telegram/notifications/toggle/
    Enables or disables notifications for the Telegram user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        if not telegram_id:
            return Response({"error": "telegram_id required"}, status=400)

        try:
            profile = TelegramProfile.objects.get(telegram_id=telegram_id)
            profile.notifications_enabled = not profile.notifications_enabled
            profile.save(update_fields=["notifications_enabled"])
            return Response({"notifications_enabled": profile.notifications_enabled})
        except TelegramProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
