"""
Signals for vacancies app.
Updates PostgreSQL SearchVector on save for FTS support.
"""

from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.vacancies.models import Vacancy


@receiver(post_save, sender=Vacancy)
def update_search_vector(sender, instance, created, **kwargs):
    """
    Update search_vector field after vacancy save.
    Uses deferred update to avoid recursive signal.
    """
    Vacancy.objects.filter(pk=instance.pk).update(
        search_vector=(
            SearchVector("title", weight="A", config="russian")
            + SearchVector("company_name", weight="B", config="russian")
            + SearchVector("description", weight="C", config="russian")
        )
    )
