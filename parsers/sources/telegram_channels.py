"""
TelegramChannelParser — Stub parser for Telegram job channels.
"""

import logging
from typing import Optional

from parsers.base import BaseParser, VacancyDTO
from parsers.registry import ParserRegistry

logger = logging.getLogger(__name__)


@ParserRegistry.register
class TelegramChannelParser(BaseParser):
    source_slug = "telegram"

    def fetch(self, page: int = 0, **kwargs) -> list[dict]:
        """TODO: Implement via Telethon/Pyrogram."""
        channels = self.config.get("channels", [])
        logger.info(f"TelegramChannelParser: {len(channels)} channels (Telethon pending)")
        return []

    def normalize(self, raw: dict) -> Optional[VacancyDTO]:
        return None
