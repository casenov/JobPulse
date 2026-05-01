import django_filters

from apps.vacancies.models import ExperienceLevel, Vacancy, WorkFormat


class VacancyFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    company = django_filters.CharFilter(field_name="company_name", lookup_expr="icontains")
    location = django_filters.CharFilter(
        field_name="location_normalized", lookup_expr="icontains"
    )
    work_format = django_filters.ChoiceFilter(choices=WorkFormat.choices)
    experience_level = django_filters.ChoiceFilter(choices=ExperienceLevel.choices)
    salary_min = django_filters.NumberFilter(field_name="salary_from", lookup_expr="gte")
    salary_max = django_filters.NumberFilter(field_name="salary_to", lookup_expr="lte")
    source = django_filters.CharFilter(field_name="source__slug")
    published_after = django_filters.DateTimeFilter(
        field_name="published_at", lookup_expr="gte"
    )
    skills = django_filters.CharFilter(method="filter_skills")

    class Meta:
        model = Vacancy
        fields = [
            "work_format", "experience_level", "employment_type", "source"
        ]

    def filter_skills(self, queryset, name, value):
        """Filter vacancies that mention a skill (case-insensitive substring of skills array)."""
        skill = value.lower()
        return queryset.filter(skills__icontains=skill)
