"""
ParsePipeline — Orchestrates the full parsing flow for one source.

Steps:
  1. fetch()       — get raw data from source (all pages)
  2. normalize()   — convert raw → VacancyDTO
  3. validate()    — reject incomplete DTOs
  4. deduplicate() — filter already-known vacancies
  5. save()        — bulk insert new vacancies
  6. log()         — write ParsingLog entry
"""

import logging
from datetime import datetime, timezone

from django.db import transaction

from apps.sources.models import LogStatus, ParsingLog, Source
from apps.vacancies.models import Vacancy, VacancyContent
from parsers.base import BaseParser, VacancyDTO
from parsers.deduplicator import Deduplicator
from parsers.normalizers import (
    detect_experience_level,
    detect_work_format,
    extract_skills,
    strip_html,
)

logger = logging.getLogger(__name__)

BULK_BATCH_SIZE = 500


class ParsePipeline:
    """
    Senior-level pipeline:
    - Fault-tolerant: individual parse errors don't kill the whole run
    - Efficient: bulk_create for inserts
    - Transactional: log always gets written
    """

    def __init__(self, source: Source, parser: BaseParser):
        self.source = source
        self.parser = parser
        self.deduplicator = Deduplicator()
        self._log: ParsingLog = None

    def run(self) -> ParsingLog:
        """Main entry point."""
        self._log = ParsingLog.objects.create(
            source=self.source,
            status=LogStatus.STARTED,
        )
        try:
            dtos = self._collect_all_pages()
            valid_dtos = self._validate(dtos)
            new_dtos = self.deduplicator.filter_new(valid_dtos)
            saved_count = self._save(new_dtos)

            self._finish_log(
                status=LogStatus.SUCCESS,
                parsed_count=len(dtos),
                new_count=saved_count,
                duplicate_count=len(valid_dtos) - saved_count,
            )
        except Exception as exc:
            logger.error(
                f"Pipeline failed for {self.source.slug}: {exc}", exc_info=True
            )
            self._finish_log(status=LogStatus.FAILED, error_message=str(exc))

        return self._log

    # ──────────────────────────────────────────────────────────────────────────

    def _collect_all_pages(self) -> list[VacancyDTO]:
        """Fetch all pages and normalize results."""
        all_dtos = []
        total_pages = self.parser.get_total_pages()

        for page in range(total_pages):
            try:
                raw_items = self.parser.fetch(page=page)
                for raw in raw_items:
                    try:
                        dto = self.parser.normalize(raw)
                        if dto is not None:
                            dto = self._enrich(dto)
                            all_dtos.append(dto)
                    except Exception as e:
                        logger.warning(f"Normalize error on page {page}: {e}")
            except Exception as e:
                logger.error(f"Fetch error on page {page}: {e}", exc_info=True)

        return all_dtos

    def _enrich(self, dto: VacancyDTO) -> VacancyDTO:
        """Post-normalize enrichment using our normalizers."""
        combined_text = f"{dto.title} {dto.description}"

        if dto.work_format == "not_specified":
            dto.work_format = detect_work_format(combined_text)

        if dto.experience_level == "not_specified":
            dto.experience_level = detect_experience_level(combined_text)

        if not dto.skills:
            dto.skills = extract_skills(combined_text)

        # Strip HTML from description
        dto.description = strip_html(dto.description)

        return dto

    def _validate(self, dtos: list[VacancyDTO]) -> list[VacancyDTO]:
        return [dto for dto in dtos if self.parser.validate(dto)]

    @transaction.atomic
    def _save(self, dtos: list[VacancyDTO]) -> int:
        """Bulk-insert vacancies and their content."""
        if not dtos:
            return 0

        vacancies = []
        for dto in dtos:
            vacancies.append(
                Vacancy(
                    external_id=dto.external_id,
                    source=self.source,
                    title=dto.title,
                    description=dto.description,
                    company_name=dto.company_name,
                    company_meta=dto.company_meta,
                    location_raw=dto.location_raw,
                    salary_from=dto.salary_from,
                    salary_to=dto.salary_to,
                    currency=dto.currency,
                    employment_type=dto.employment_type,
                    work_format=dto.work_format,
                    experience_level=dto.experience_level,
                    skills=dto.skills,
                    url=dto.url,
                    published_at=dto.published_at,
                )
            )

        created = Vacancy.objects.bulk_create(
            vacancies,
            batch_size=BULK_BATCH_SIZE,
            ignore_conflicts=True,  # skip on URL unique constraint violation
        )

        # Save full text content separately
        if created:
            dto_map = {dto.url: dto for dto in dtos}
            contents = [
                VacancyContent(
                    vacancy=v,
                    full_text=dto_map.get(v.url, VacancyDTO("", "", "", "")).description,
                )
                for v in created
            ]
            VacancyContent.objects.bulk_create(
                contents,
                batch_size=BULK_BATCH_SIZE,
                ignore_conflicts=True,
            )

        # Update source last_parsed_at
        Source.objects.filter(pk=self.source.pk).update(
            last_parsed_at=datetime.now(tz=timezone.utc)
        )

        return len(created)

    def _finish_log(
        self,
        status: str,
        parsed_count: int = 0,
        new_count: int = 0,
        duplicate_count: int = 0,
        error_message: str = None,
    ):
        from django.utils import timezone as dj_timezone

        ParsingLog.objects.filter(pk=self._log.pk).update(
            status=status,
            parsed_count=parsed_count,
            new_count=new_count,
            duplicate_count=duplicate_count,
            error_message=error_message,
            finished_at=dj_timezone.now(),
        )
