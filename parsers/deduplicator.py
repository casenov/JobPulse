"""
Deduplicator — Prevents duplicate vacancies from being saved.

Strategies:
1. URL uniqueness (primary — enforced by DB unique constraint)
2. (source, external_id) pair uniqueness
3. Fuzzy title + company matching (optional, for cross-source dedup)
"""

import logging

from django.db.models import Q

from apps.vacancies.models import Vacancy
from parsers.base import VacancyDTO

logger = logging.getLogger(__name__)


class Deduplicator:
    """
    Filters out VacancyDTOs that already exist in the database.
    Works on batches for efficiency.
    """

    def filter_new(self, dtos: list[VacancyDTO]) -> list[VacancyDTO]:
        """
        Return only DTOs that are not yet in the database.
        Uses batch DB query — O(1) queries regardless of batch size.
        """
        if not dtos:
            return []

        urls = {dto.url for dto in dtos}
        ext_ids = {
            (dto.source_slug, dto.external_id)
            for dto in dtos
            if dto.external_id
        }

        # Build URL set of existing vacancies
        existing_urls = set(
            Vacancy.all_objects.filter(url__in=urls).values_list("url", flat=True)
        )

        # Build (source_slug, external_id) set
        if ext_ids:
            q = Q()
            for source_slug, ext_id in ext_ids:
                q |= Q(source__slug=source_slug, external_id=ext_id)
            existing_ext = set(
                Vacancy.all_objects.filter(q)
                .values_list("source__slug", "external_id")
            )
        else:
            existing_ext = set()

        new_dtos = []
        duplicates = 0
        for dto in dtos:
            if dto.url in existing_urls:
                duplicates += 1
                continue
            if (dto.source_slug, dto.external_id) in existing_ext:
                duplicates += 1
                continue
            new_dtos.append(dto)

        logger.debug(
            f"Deduplicator: {len(dtos)} total, "
            f"{len(new_dtos)} new, {duplicates} duplicates."
        )
        return new_dtos
