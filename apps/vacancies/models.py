import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models

from apps.sources.models import Source
from core.mixins import SoftDeleteModel, TimestampedModel


class EmploymentType(models.TextChoices):
    FULL_TIME = "full_time", "Full-time"
    PART_TIME = "part_time", "Part-time"
    CONTRACT = "contract", "Contract"
    FREELANCE = "freelance", "Freelance"
    INTERNSHIP = "internship", "Internship"


class WorkFormat(models.TextChoices):
    REMOTE = "remote", "Remote"
    ONSITE = "onsite", "On-site"
    HYBRID = "hybrid", "Hybrid"
    NOT_SPECIFIED = "not_specified", "Not specified"


class ExperienceLevel(models.TextChoices):
    INTERN = "intern", "Intern"
    JUNIOR = "junior", "Junior"
    MIDDLE = "middle", "Middle"
    SENIOR = "senior", "Senior"
    LEAD = "lead", "Lead"
    NOT_SPECIFIED = "not_specified", "Not specified"


class Vacancy(TimestampedModel, SoftDeleteModel):
    """
    Core vacancy model.
    Designed for high-volume inserts and full-text search.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    source = models.ForeignKey(
        Source, on_delete=models.PROTECT, related_name="vacancies"
    )

    # Core fields
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True, default="")
    company_name = models.CharField(max_length=255, blank=True, default="")
    company_meta = models.JSONField(default=dict, blank=True)  # logo_url, website, etc.

    # Location
    location_raw = models.CharField(max_length=500, blank=True, default="")
    location_normalized = models.CharField(max_length=255, null=True, blank=True)

    # Salary
    salary_from = models.IntegerField(null=True, blank=True)
    salary_to = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, default="RUB")

    # Classification
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    work_format = models.CharField(
        max_length=20,
        choices=WorkFormat.choices,
        default=WorkFormat.NOT_SPECIFIED,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.NOT_SPECIFIED,
    )

    # Skills extracted from description
    skills = models.JSONField(default=list, blank=True)

    # Source reference
    url = models.URLField(max_length=2048, unique=True)
    published_at = models.DateTimeField(null=True, blank=True)

    # FTS
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        verbose_name = "Vacancy"
        verbose_name_plural = "Vacancies"
        ordering = ["-published_at"]
        indexes = [
            GinIndex(fields=["search_vector"], name="vacancy_search_gin"),
            models.Index(fields=["published_at"], name="vacancy_published_idx"),
            models.Index(fields=["source", "external_id"], name="vacancy_source_ext_idx"),
            models.Index(fields=["experience_level"], name="vacancy_level_idx"),
            models.Index(fields=["work_format"], name="vacancy_format_idx"),
            models.Index(fields=["salary_from", "salary_to"], name="vacancy_salary_idx"),
            models.Index(fields=["is_deleted", "is_active"], name="vacancy_active_idx"),
        ]
        unique_together = [("source", "external_id")]

    def __str__(self):
        return f"{self.title} @ {self.company_name}"

    @property
    def salary_display(self):
        if self.salary_from and self.salary_to:
            return f"{self.salary_from:,} – {self.salary_to:,} {self.currency}"
        if self.salary_from:
            return f"от {self.salary_from:,} {self.currency}"
        if self.salary_to:
            return f"до {self.salary_to:,} {self.currency}"
        return "Не указана"


class VacancyContent(models.Model):
    """
    Separate table for heavy text content.
    Allows keeping the main Vacancy table lean for index scans.
    """

    vacancy = models.OneToOneField(
        Vacancy, on_delete=models.CASCADE, related_name="content", primary_key=True
    )
    full_html = models.TextField(blank=True, default="")
    full_text = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Vacancy Content"
        verbose_name_plural = "Vacancy Contents"
