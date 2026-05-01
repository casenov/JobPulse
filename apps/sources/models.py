from django.db import models

from core.mixins import TimestampedModel


class SourceType(models.TextChoices):
    API = "api", "API"
    SCRAPING = "scraping", "Web Scraping"
    TELEGRAM = "telegram", "Telegram Channel"
    RSS = "rss", "RSS Feed"


class Source(TimestampedModel):
    """
    Represents a job vacancy source (hh.ru, LinkedIn, etc.)
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    source_type = models.CharField(
        max_length=20, choices=SourceType.choices, default=SourceType.API
    )
    base_url = models.URLField()
    rate_limit = models.PositiveIntegerField(
        default=1, help_text="Max requests per second"
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Source-specific configuration (API keys, headers, etc.)",
    )
    is_active = models.BooleanField(default=True)
    last_parsed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Source"
        verbose_name_plural = "Sources"
        ordering = ["name"]

    def __str__(self):
        return self.name


class LogStatus(models.TextChoices):
    STARTED = "started", "Started"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    PARTIAL = "partial", "Partial"


class ParsingLog(models.Model):
    """
    Log entry for each parsing run.
    Used for monitoring and debugging.
    """

    source = models.ForeignKey(
        Source, on_delete=models.CASCADE, related_name="parsing_logs"
    )
    status = models.CharField(
        max_length=20, choices=LogStatus.choices, default=LogStatus.STARTED
    )
    parsed_count = models.IntegerField(default=0)
    new_count = models.IntegerField(default=0)
    duplicate_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Parsing Log"
        verbose_name_plural = "Parsing Logs"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["source", "started_at"], name="parselog_source_idx"),
            models.Index(fields=["status"], name="parselog_status_idx"),
        ]

    def __str__(self):
        return f"{self.source.name} — {self.status} @ {self.started_at:%Y-%m-%d %H:%M}"

    @property
    def duration_seconds(self):
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None
