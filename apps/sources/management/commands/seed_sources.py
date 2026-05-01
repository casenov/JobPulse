"""
Management command: seed_sources
Seeds the database with initial Source records.
Usage: python manage.py seed_sources
"""

from django.core.management.base import BaseCommand

from apps.sources.models import Source, SourceType

SOURCES = [
    {
        "name": "HeadHunter",
        "slug": "hh",
        "source_type": SourceType.API,
        "base_url": "https://api.hh.ru",
        "rate_limit": 3,
        "is_active": True,
        "config": {
            "params": {
                "text": "python OR django OR fastapi OR backend",
                "area": 113,
                "per_page": 100,
            }
        },
    },
    {
        "name": "Telegram Channels",
        "slug": "telegram",
        "source_type": SourceType.TELEGRAM,
        "base_url": "https://t.me",
        "rate_limit": 1,
        "is_active": False,  # enable after Telethon setup
        "config": {
            "channels": ["pythondjango_jobs", "it_jobs_ru"]
        },
    },
]


class Command(BaseCommand):
    help = "Seed initial source records"

    def handle(self, *args, **options):
        created_count = 0
        for data in SOURCES:
            obj, created = Source.objects.update_or_create(
                slug=data["slug"],
                defaults=data,
            )
            status = "created" if created else "updated"
            self.stdout.write(f"  {status}: {obj.name}")
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Done. {created_count} new sources created."
            )
        )
