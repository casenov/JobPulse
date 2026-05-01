import logging

from celery import shared_task

from apps.matching.engine import MatchingEngine

logger = logging.getLogger(__name__)


@shared_task(
    name="apps.matching.tasks.run_matching_engine",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def run_matching_engine(self, since_hours: int = 1):
    """
    Run the full matching engine for vacancies parsed in the last N hours.
    """
    try:
        engine = MatchingEngine(since_hours=since_hours)
        result = engine.run()
        logger.info(f"Matching engine completed: {result}")
        return result
    except Exception as exc:
        logger.error(f"Matching engine failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)
