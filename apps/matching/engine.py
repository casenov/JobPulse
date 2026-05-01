"""
MatchingEngine — orchestrates the full matching pipeline.

Flow:
1. Load all active filters
2. Load unmatched vacancies (recently parsed)
3. For each (vacancy, filter) pair — compute score
4. Bulk-insert VacancyMatch rows above threshold
"""

import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.filters.models import UserFilter
from apps.matching.models import VacancyMatch
from apps.matching.scoring import MIN_SCORE_THRESHOLD, compute_score
from apps.vacancies.models import Vacancy

logger = logging.getLogger(__name__)


class MatchingEngine:
    """
    Senior-level implementation:
    - Processes in batches to avoid memory exhaustion
    - Uses bulk_create with update_conflicts for idempotency
    - Logs progress
    """

    VACANCY_BATCH_SIZE = 500
    MATCH_BATCH_SIZE = 1000

    def __init__(self, since_hours: int = 1):
        """
        :param since_hours: Only match vacancies parsed in the last N hours.
        """
        self.since = timezone.now() - timedelta(hours=since_hours)

    def run(self) -> dict:
        """
        Main entry point. Returns statistics.
        """
        filters = self._get_active_filters()
        if not filters:
            logger.info("MatchingEngine: no active filters, skipping.")
            return {"matches_created": 0, "vacancies_processed": 0}

        logger.info(f"MatchingEngine: {len(filters)} active filters loaded.")

        total_vacancies = 0
        total_matches = 0

        qs = self._get_vacancies_queryset()

        # Process in batches
        offset = 0
        while True:
            batch = list(qs[offset : offset + self.VACANCY_BATCH_SIZE])
            if not batch:
                break

            matches = self._match_batch(batch, filters)
            created = self._save_matches(matches)

            total_vacancies += len(batch)
            total_matches += created
            offset += self.VACANCY_BATCH_SIZE

            logger.debug(
                f"MatchingEngine: processed {total_vacancies} vacancies, "
                f"{total_matches} matches so far."
            )

        logger.info(
            f"MatchingEngine: done. {total_vacancies} vacancies, "
            f"{total_matches} matches created/updated."
        )
        return {
            "matches_created": total_matches,
            "vacancies_processed": total_vacancies,
        }

    def _get_active_filters(self) -> list[UserFilter]:
        return list(
            UserFilter.objects.filter(is_active=True).select_related("user")
        )

    def _get_vacancies_queryset(self):
        return (
            Vacancy.objects.filter(
                is_deleted=False,
                created_at__gte=self.since,
            )
            .select_related("source")
            .only(
                "id",
                "title",
                "description",
                "location_raw",
                "location_normalized",
                "work_format",
                "experience_level",
                "salary_from",
                "salary_to",
            )
        )

    def _match_batch(
        self, vacancies: list[Vacancy], filters: list[UserFilter]
    ) -> list[VacancyMatch]:
        """
        Compute scores for all (vacancy, filter) combinations in this batch.
        """
        results = []
        for vacancy in vacancies:
            for user_filter in filters:
                result = compute_score(vacancy, user_filter)
                if result.total >= MIN_SCORE_THRESHOLD:
                    results.append(
                        VacancyMatch(
                            vacancy=vacancy,
                            filter=user_filter,
                            **result.to_dict(),
                        )
                    )
        return results

    @transaction.atomic
    def _save_matches(self, matches: list[VacancyMatch]) -> int:
        """
        Bulk-insert matches. If (vacancy, filter) already exists — update score.
        """
        if not matches:
            return 0

        created = VacancyMatch.objects.bulk_create(
            matches,
            batch_size=self.MATCH_BATCH_SIZE,
            update_conflicts=True,
            unique_fields=["vacancy", "filter"],
            update_fields=["score", "keyword_score", "location_score", "salary_score", "experience_score"],
        )
        return len(created)
