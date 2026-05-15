from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes

from apps.vacancies.models import Vacancy


class VacancyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list view — no heavy description field."""

    source_name = serializers.CharField(source="source.name", read_only=True)
    @extend_schema_field(OpenApiTypes.STR)
    def get_salary_display(self, obj):
        return obj.salary_display

    salary_display = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            "id", "title", "company_name", "source_name",
            "location_normalized", "location_raw",
            "work_format", "experience_level", "employment_type",
            "salary_from", "salary_to", "currency", "salary_display",
            "skills", "url", "published_at",
        ]


class VacancyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail view — includes description and content."""

    source_name = serializers.CharField(source="source.name", read_only=True)
    @extend_schema_field(OpenApiTypes.STR)
    def get_salary_display(self, obj):
        return obj.salary_display

    salary_display = serializers.SerializerMethodField()
    full_text = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            "id", "title", "company_name", "company_meta", "source_name",
            "location_raw", "location_normalized",
            "work_format", "experience_level", "employment_type",
            "salary_from", "salary_to", "currency", "salary_display",
            "description", "full_text", "skills",
            "url", "published_at", "created_at",
        ]

    @extend_schema_field(OpenApiTypes.STR)
    def get_full_text(self, obj):
        if hasattr(obj, "content"):
            return obj.content.full_text
        return None
