"""
Celery tasks for the parser system.
"""

import logging

from celery import shared_task
from django.db.models import Q

from apps.sources.models import Source

logger = logging.getLogger(__name__)


@shared_task(
    name="parsers.tasks.parse_source",
    bind=True,
    max_retries=3,
    default_retry_delay=120,
)
def parse_source(self, source_slug: str):
    """
    Parse a single source by slug.
    Loads the parser from registry, runs the pipeline.
    """
    from parsers.pipeline import ParsePipeline
    from parsers.registry import ParserRegistry, autodiscover

    autodiscover()

    try:
        source = Source.objects.get(slug=source_slug, is_active=True)
    except Source.DoesNotExist:
        logger.warning(f"Source '{source_slug}' not found or inactive.")
        return

    try:
        parser_class = ParserRegistry.get(source_slug)
        parser = parser_class(config=source.config)
        pipeline = ParsePipeline(source=source, parser=parser)
        log = pipeline.run()
        logger.info(
            f"parse_source({source_slug}): "
            f"status={log.status}, new={log.new_count}, dupes={log.duplicate_count}"
        )
        return {
            "source": source_slug,
            "status": log.status,
            "new_count": log.new_count,
        }
    except KeyError:
        logger.error(f"No parser registered for slug '{source_slug}'")
    except Exception as exc:
        logger.error(f"parse_source({source_slug}) failed: {exc}", exc_info=True)
        raise self.retry(exc=exc)


@shared_task(name="parsers.tasks.parse_all_sources")
def parse_all_sources():
    """
    Trigger parsing for all active sources.
    Dispatches individual parse_source tasks.
    """
    slugs = Source.objects.filter(is_active=True).values_list("slug", flat=True)
    if not slugs:
        logger.info("parse_all_sources: no active sources found.")
        return

    for slug in slugs:
        parse_source.delay(slug)
        logger.info(f"parse_all_sources: dispatched task for '{slug}'")

    return {"dispatched": list(slugs)}


@shared_task(name="parsers.tasks.cleanup_old_vacancies")
def cleanup_old_vacancies(days: int = 90):
    """
    Soft-delete vacancies older than N days that have no matches.
    """
    from datetime import timedelta

    from django.utils import timezone

    from apps.vacancies.models import Vacancy

    cutoff = timezone.now() - timedelta(days=days)
    updated = (
        Vacancy.objects.filter(
            published_at__lt=cutoff,
            is_deleted=False,
            matches__isnull=True,
        )
        .update(is_deleted=True)
    )
    logger.info(f"cleanup_old_vacancies: soft-deleted {updated} old vacancies.")
    return {"deleted": updated}
