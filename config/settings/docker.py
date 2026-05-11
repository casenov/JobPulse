"""
JobPulse Docker settings — for local Docker development.
Like production but without SSL redirect and with relaxed security.
"""
from .base import *  # noqa

DEBUG = False

# No SSL redirect — we're running plain HTTP on port 8000 locally
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Sentry (optional, won't break if not configured)
try:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    _sentry_dsn = env("SENTRY_DSN", default="")  # noqa
    if _sentry_dsn:
        sentry_sdk.init(
            dsn=_sentry_dsn,
            integrations=[DjangoIntegration(), CeleryIntegration()],
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
except ImportError:
    pass
