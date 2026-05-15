from django.db.models import F
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
from drf_spectacular.utils import extend_schema

from apps.vacancies.filters import VacancyFilter
from apps.vacancies.models import Vacancy
from apps.vacancies.serializers import VacancyDetailSerializer, VacancyListSerializer


class VacancyListView(generics.ListAPIView):
    """
    Возвращает список вакансий с пагинацией, фильтрацией и поиском.
    """

    serializer_class = VacancyListSerializer
    filterset_class = VacancyFilter
    permission_classes = [AllowAny]
    search_fields = ["title", "company_name", "description"]
    ordering_fields = ["published_at", "salary_from", "created_at"]
    ordering = ["-published_at"]

    def get_queryset(self):
        qs = (
            Vacancy.objects.filter(is_deleted=False)
            .select_related("source")
            .only(
                "id", "title", "company_name", "source",
                "location_raw", "location_normalized",
                "work_format", "experience_level", "employment_type",
                "salary_from", "salary_to", "currency",
                "skills", "url", "published_at",
            )
        )

        # Search
        q = self.request.query_params.get("q")
        if q:
            # Fallback for SQLite (icontains) since SearchVector is Postgres-only
            from django.db.models import Q
            qs = qs.filter(
                Q(title__icontains=q) | 
                Q(company_name__icontains=q) | 
                Q(description__icontains=q)
            )

        return qs


class VacancyDetailView(generics.RetrieveAPIView):
    """
    Возвращает полную информацию о вакансии, включая описание.
    """

    serializer_class = VacancyDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return (
            Vacancy.objects.filter(is_deleted=False)
            .select_related("source", "content")
        )


class VacancyStatsView(APIView):
    """
    Агрегированная статистика для панели управления.
    """

    permission_classes = [AllowAny]

    @extend_schema(responses={200: serializers.DictField()})
    def get(self, request):
        from django.db.models import Count, Max

        stats = Vacancy.objects.filter(is_deleted=False).aggregate(
            total=Count("id"),
            latest=Max("published_at"),
        )
        by_level = (
            Vacancy.objects.filter(is_deleted=False)
            .values("experience_level")
            .annotate(count=Count("id"))
        )
        by_format = (
            Vacancy.objects.filter(is_deleted=False)
            .values("work_format")
            .annotate(count=Count("id"))
        )
        return Response(
            {
                "total": stats["total"],
                "latest_published_at": stats["latest"],
                "by_experience_level": list(by_level),
                "by_work_format": list(by_format),
            }
        )
