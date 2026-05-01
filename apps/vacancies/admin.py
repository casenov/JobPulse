from django.contrib import admin

from .models import VacancyContent, Vacancy


class VacancyContentInline(admin.StackedInline):
    model = VacancyContent
    extra = 0
    readonly_fields = ["full_text", "full_html"]


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = [
        "title", "company_name", "source", "experience_level",
        "work_format", "salary_display", "published_at", "is_deleted"
    ]
    list_filter = [
        "source", "experience_level", "work_format", "employment_type", "is_deleted"
    ]
    search_fields = ["title", "company_name", "location_raw"]
    readonly_fields = ["id", "created_at", "updated_at", "search_vector"]
    raw_id_fields = ["source"]
    ordering = ["-published_at"]
    date_hierarchy = "published_at"
    inlines = [VacancyContentInline]

    fieldsets = (
        ("Core", {
            "fields": ("id", "title", "company_name", "company_meta", "url", "source", "external_id")
        }),
        ("Classification", {
            "fields": ("experience_level", "work_format", "employment_type", "skills")
        }),
        ("Location", {
            "fields": ("location_raw", "location_normalized")
        }),
        ("Salary", {
            "fields": ("salary_from", "salary_to", "currency")
        }),
        ("Dates", {
            "fields": ("published_at", "created_at", "updated_at")
        }),
        ("State", {
            "fields": ("is_deleted", "search_vector")
        }),
    )
