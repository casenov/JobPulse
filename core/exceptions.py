import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        response.data = {
            "error": True,
            "status_code": response.status_code,
            "detail": response.data,
        }
    else:
        logger.exception("Unhandled exception", exc_info=exc)

    return response
