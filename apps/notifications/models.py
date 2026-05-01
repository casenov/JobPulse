from django.db import models

from apps.matching.models import VacancyMatch
from apps.users.models import User
from core.mixins import TimestampedModel


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    SKIPPED = "skipped", "Skipped"


class NotificationQueue(TimestampedModel):
    """
    Queue for outgoing notifications.
    Decoupled from matching so we can retry failed sends.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    match = models.OneToOneField(
        VacancyMatch,
        on_delete=models.CASCADE,
        related_name="notification",
        null=True,
        blank=True,
    )
    channel = models.CharField(
        max_length=20,
        default="telegram",
        help_text="Delivery channel: telegram, email, etc.",
    )
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    retry_count = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["status", "channel"],
                name="notif_status_channel_idx",
            ),
        ]

    def __str__(self):
        return f"Notification for {self.user} [{self.status}]"
