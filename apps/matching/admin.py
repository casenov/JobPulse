from django.contrib import admin

from .models import VacancyMatch


@admin.register(VacancyMatch)
class VacancyMatchAdmin(admin.ModelAdmin):
    list_display = [
        "vacancy", "filter", "score", "keyword_score",
        "location_score", "salary_score", "is_notified", "created_at"
    ]
    list_filter = ["is_notified"]
    search_fields = ["vacancy__title", "filter__user__email"]
    raw_id_fields = ["vacancy", "filter"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-score"]
