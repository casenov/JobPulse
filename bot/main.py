"""
Telegram Bot entry point (aiogram 3.x).
Run: python -m bot.main
"""

import asyncio
import logging
import os
import sys

# Add project root to path so Django settings can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from django.conf import settings

from bot.handlers import filters, start, status
from bot.middlewares.auth import TelegramAuthMiddleware

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register middlewares
    dp.message.middleware(TelegramAuthMiddleware())
    dp.callback_query.middleware(TelegramAuthMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(filters.router)
    dp.include_router(status.router)

    logger.info("JobScout Bot started.")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
