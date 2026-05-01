"""
Notification tasks — sends pending notifications via Telegram.
"""

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    name="apps.notifications.tasks.send_pending_notifications",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_pending_notifications(self):
    """
    Find all pending VacancyMatch notifications and send them via Telegram.
    """
    from apps.notifications.models import NotificationQueue, NotificationStatus
    from apps.notifications.backends.telegram import TelegramBackend

    pending = (
        NotificationQueue.objects.filter(
            status=NotificationStatus.PENDING,
            channel="telegram",
            retry_count__lt=3,
        )
        .select_related("user__telegram_profile", "match__vacancy")
        .order_by("created_at")[:100]  # process in batches of 100
    )

    if not pending:
        logger.debug("send_pending_notifications: nothing to send.")
        return {"sent": 0}

    backend = TelegramBackend()
    sent = 0
    failed = 0

    for notification in pending:
        try:
            backend.send(notification)
            sent += 1
        except Exception as exc:
            logger.error(f"Failed to send notification {notification.id}: {exc}")
            failed += 1

    logger.info(f"send_pending_notifications: sent={sent}, failed={failed}")
    return {"sent": sent, "failed": failed}


@shared_task(name="apps.notifications.tasks.enqueue_matches")
def enqueue_matches():
    """
    Convert unnotified VacancyMatch records into NotificationQueue entries.
    """
    from django.utils import timezone

    from apps.matching.models import VacancyMatch
    from apps.notifications.models import NotificationQueue

    unnotified = VacancyMatch.objects.filter(
        is_notified=False,
        filter__user__telegram_profile__notifications_enabled=True,
    ).select_related("filter__user__telegram_profile")

    queue_items = []
    for match in unnotified:
        user = match.filter.user
        if not hasattr(user, "telegram_profile"):
            continue
        queue_items.append(
            NotificationQueue(
                user=user,
                match=match,
                channel="telegram",
            )
        )

    if queue_items:
        NotificationQueue.objects.bulk_create(
            queue_items,
            ignore_conflicts=True,
            batch_size=500,
        )
        VacancyMatch.objects.filter(
            id__in=[m.id for m in unnotified]
        ).update(is_notified=True)
        logger.info(f"enqueue_matches: enqueued {len(queue_items)} notifications.")

    return {"enqueued": len(queue_items)}
