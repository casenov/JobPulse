from django.contrib import admin

from .models import TelegramProfile, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "email", "is_active", "is_staff", "created_at"]
    list_filter = ["is_active", "is_staff"]
    search_fields = ["email"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = [
        "telegram_id", "username", "user", "notifications_enabled", "last_active_at"
    ]
    list_filter = ["notifications_enabled"]
    search_fields = ["telegram_id", "username", "user__email"]
    raw_id_fields = ["user"]
