from django.urls import path

from apps.users.views import (
    MeView,
    TelegramRegisterView,
    TelegramToggleNotificationsView,
)

urlpatterns = [
    path("me/", MeView.as_view(), name="user-me"),
    path("telegram/register/", TelegramRegisterView.as_view(), name="telegram-register"),
    path(
        "telegram/notifications/toggle/",
        TelegramToggleNotificationsView.as_view(),
        name="telegram-notifications-toggle",
    ),
]
