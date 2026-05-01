"""
TelegramBackend — sends vacancy notifications to Telegram users.
Uses synchronous httpx (called from Celery worker).
"""

import logging

import httpx
from django.conf import settings

from apps.notifications.models import NotificationQueue, NotificationStatus

logger = logging.getLogger(__name__)


class TelegramBackend:
    API_URL = "https://api.telegram.org/bot{token}/sendMessage"

    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.url = self.API_URL.format(token=self.token)

    def send(self, notification: NotificationQueue):
        """
        Send a single vacancy notification via Telegram Bot API.
        Updates the notification status.
        """
        from django.utils import timezone

        vacancy = notification.match.vacancy
        profile = notification.user.telegram_profile

        text = self._format_vacancy(vacancy)

        try:
            resp = httpx.post(
                self.url,
                json={
                    "chat_id": profile.telegram_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=10.0,
            )
            resp.raise_for_status()

            NotificationQueue.objects.filter(pk=notification.pk).update(
                status=NotificationStatus.SENT,
                sent_at=timezone.now(),
            )

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            self._mark_failed(notification, error_msg)
            raise

        except httpx.RequestError as e:
            self._mark_failed(notification, str(e))
            raise

    def _format_vacancy(self, vacancy) -> str:
        """Format vacancy as a clean Telegram message."""
        lines = [
            f"🆕 <b>{vacancy.title}</b>",
            f"🏢 {vacancy.company_name or 'Компания не указана'}",
        ]

        if vacancy.location_normalized or vacancy.location_raw:
            loc = vacancy.location_normalized or vacancy.location_raw
            lines.append(f"📍 {loc}")

        if vacancy.work_format != "not_specified":
            fmt_map = {"remote": "🌐 Удалённо", "onsite": "🏢 Офис", "hybrid": "🔀 Гибрид"}
            lines.append(fmt_map.get(vacancy.work_format, ""))

        if vacancy.salary_display != "Не указана":
            lines.append(f"💰 {vacancy.salary_display}")

        if vacancy.skills:
            lines.append(f"🛠 {', '.join(vacancy.skills[:6])}")

        lines.append(f"\n🔗 <a href='{vacancy.url}'>Открыть вакансию</a>")

        return "\n".join(filter(None, lines))

    def _mark_failed(self, notification: NotificationQueue, error: str):
        NotificationQueue.objects.filter(pk=notification.pk).update(
            status=NotificationStatus.FAILED,
            error=error,
            retry_count=notification.retry_count + 1,
        )
