from django.db import models

from apps.filters.models import UserFilter
from apps.vacancies.models import Vacancy
from core.mixins import TimestampedModel


class VacancyMatch(TimestampedModel):
    """
    Result of matching engine run.
    Stores which vacancy matched which user filter and the match score.
    """

    vacancy = models.ForeignKey(
        Vacancy, on_delete=models.CASCADE, related_name="matches"
    )
    filter = models.ForeignKey(
        UserFilter, on_delete=models.CASCADE, related_name="matches"
    )
    score = models.FloatField(help_text="Match score from 0.0 to 1.0")
    keyword_score = models.FloatField(default=0.0)
    location_score = models.FloatField(default=0.0)
    salary_score = models.FloatField(default=0.0)
    experience_score = models.FloatField(default=0.0)
    is_notified = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Vacancy Match"
        verbose_name_plural = "Vacancy Matches"
        unique_together = [("vacancy", "filter")]
        ordering = ["-score", "-created_at"]
        indexes = [
            models.Index(fields=["filter", "is_notified"], name="match_filter_notified_idx"),
            models.Index(fields=["score"], name="match_score_idx"),
        ]

    def __str__(self):
        return f"{self.vacancy.title} ↔ {self.filter} (score={self.score:.2f})"
