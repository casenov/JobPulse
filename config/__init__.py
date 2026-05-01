# This file is intentionally left empty.
# It triggers Celery autodiscover when the package is imported.
from .celery import app as celery_app

__all__ = ["celery_app"]
