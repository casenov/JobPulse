"""
Telegram auth middleware — registers or fetches user on every message.
"""

from typing import Any, Awaitable, Callable

import httpx
from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class TelegramAuthMiddleware(BaseMiddleware):
    """
    Intercepts every update, calls our API to register/update the user,
    and injects user data into handler data dict.
    """

    API_URL = "http://localhost:8000/api/v1/users/telegram/register/"

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        from_user = None
        if hasattr(event, "from_user"):
            from_user = event.from_user
        elif hasattr(event, "message") and event.message:
            from_user = event.message.from_user

        if from_user:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        self.API_URL,
                        json={
                            "telegram_id": from_user.id,
                            "username": from_user.username or "",
                            "first_name": from_user.first_name or "",
                            "last_name": from_user.last_name or "",
                            "language_code": from_user.language_code or "",
                        },
                        timeout=5.0,
                    )
                    if resp.status_code in (200, 201):
                        data["tg_user"] = resp.json().get("user")
            except Exception:
                pass  # Don't block the update if API is unavailable

        return await handler(event, data)
