from django.contrib.postgres.fields import ArrayField
from django.db import models

from apps.users.models import User
from apps.vacancies.models import ExperienceLevel, WorkFormat
from core.mixins import TimestampedModel


class UserFilter(TimestampedModel):
    """
    User-defined filter for matching vacancies.
    Each user can have multiple named filters (saved searches).
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="filters")
    name = models.CharField(max_length=255, default="Default Filter")

    # Keywords
    keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Vacancy must match at least one keyword",
    )
    excluded_keywords = models.JSONField(
        default=list,
        blank=True,
        help_text="Vacancy must NOT contain these keywords",
    )

    # Location
    locations = models.JSONField(
        default=list,
        blank=True,
        help_text="Acceptable locations (city, country)",
    )

    # Work preferences
    work_format = models.CharField(
        max_length=20,
        choices=WorkFormat.choices,
        null=True,
        blank=True,
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        null=True,
        blank=True,
    )

    # Salary
    salary_min = models.IntegerField(null=True, blank=True)

    # State
    is_active = models.BooleanField(default=True)
    notify_on_match = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User Filter"
        verbose_name_plural = "User Filters"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"], name="filter_user_active_idx"),
        ]

    def __str__(self):
        return f"{self.user} — {self.name}"
