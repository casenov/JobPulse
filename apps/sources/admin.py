from django.contrib import admin

from .models import ParsingLog, Source


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "source_type", "is_active", "last_parsed_at", "rate_limit"]
    list_filter = ["source_type", "is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at", "last_parsed_at"]


@admin.register(ParsingLog)
class ParsingLogAdmin(admin.ModelAdmin):
    list_display = [
        "source", "status", "parsed_count", "new_count",
        "duplicate_count", "started_at", "duration_seconds"
    ]
    list_filter = ["status", "source"]
    search_fields = ["source__name"]
    readonly_fields = ["started_at", "finished_at"]
    ordering = ["-started_at"]
