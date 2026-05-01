"""
HHParser — Parser for hh.ru using the official public API.
Docs: https://api.hh.ru/openapi/redoc

Rate limits: ~3-5 req/sec without auth token.
"""

import logging
from datetime import datetime
from typing import Optional

import httpx
from django.conf import settings

from parsers.base import BaseParser, VacancyDTO
from parsers.normalizers import normalize_currency
from parsers.registry import ParserRegistry

logger = logging.getLogger(__name__)

HH_API_BASE = getattr(settings, "HH_API_BASE_URL", "https://api.hh.ru")
HH_DEFAULT_PARAMS = {
    "text": "python OR django OR backend",
    "area": 113,  # Russia
    "per_page": 100,
    "search_field": "name",
}


@ParserRegistry.register
class HHParser(BaseParser):
    source_slug = "hh"

    def __init__(self, config: dict = None):
        super().__init__(config)
        self._client = httpx.Client(
            base_url=HH_API_BASE,
            headers={
                "User-Agent": "JobScout/1.0 (contact: admin@jobscout.dev)",
                "HH-User-Agent": "JobScout/1.0 (admin@jobscout.dev)",
            },
            timeout=15.0,
        )
        self._total_pages: Optional[int] = None
        self._search_params = {**HH_DEFAULT_PARAMS, **self.config.get("params", {})}

    def get_total_pages(self) -> int:
        """Probe first page to get total pages count."""
        if self._total_pages is None:
            resp = self._get_page(0)
            self._total_pages = resp.get("pages", 1)
            logger.info(f"HHParser: {self._total_pages} pages found.")
        return self._total_pages

    def fetch(self, page: int = 0, **kwargs) -> list[dict]:
        """Fetch one page of vacancies from hh.ru API."""
        resp = self._get_page(page)
        items = resp.get("items", [])
        logger.debug(f"HHParser: page {page}, got {len(items)} items.")
        return items

    def normalize(self, raw: dict) -> Optional[VacancyDTO]:
        """Convert hh.ru API item → VacancyDTO."""
        try:
            salary = raw.get("salary") or {}
            area = raw.get("area") or {}
            employer = raw.get("employer") or {}
            snippet = raw.get("snippet") or {}

            salary_from = salary.get("from")
            salary_to = salary.get("to")
            currency = normalize_currency(salary.get("currency", "RUB"))

            published_at = None
            if raw.get("published_at"):
                try:
                    published_at = datetime.fromisoformat(raw["published_at"])
                except ValueError:
                    pass

            return VacancyDTO(
                external_id=str(raw["id"]),
                title=raw.get("name", ""),
                url=raw.get("alternate_url", raw.get("url", "")),
                source_slug=self.source_slug,
                description=snippet.get("responsibility", "")
                + " "
                + snippet.get("requirement", ""),
                company_name=employer.get("name", ""),
                company_meta={
                    "logo": employer.get("logo_urls", {}).get("90"),
                    "website": employer.get("alternate_url"),
                    "trusted": employer.get("trusted", False),
                },
                location_raw=area.get("name", ""),
                salary_from=int(salary_from) if salary_from else None,
                salary_to=int(salary_to) if salary_to else None,
                currency=currency,
                published_at=published_at,
            )
        except (KeyError, TypeError, ValueError) as e:
            logger.warning(f"HHParser normalize error: {e} | raw={raw.get('id')}")
            return None

    def _get_page(self, page: int) -> dict:
        """Internal method for API request with retry."""
        params = {**self._search_params, "page": page}
        try:
            resp = self._client.get("/vacancies", params=params)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HHParser HTTP error: {e.response.status_code}")
            raise
        except httpx.RequestError as e:
            logger.error(f"HHParser request error: {e}")
            raise

    def __del__(self):
        self._client.close()
