import logging

from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import render

logger = logging.getLogger(__name__)


SCHEMA_ERROR_MARKERS = (
    "no such column",
    "no such table",
    "undefinedcolumn",
    "undefinedtable",
    "does not exist",
)


class DatabaseSchemaGuardMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except (OperationalError, ProgrammingError) as exc:
            message = str(exc).lower()
            if any(marker in message for marker in SCHEMA_ERROR_MARKERS):
                logger.exception("Database schema mismatch detected", extra={"path": request.path})
                response = render(
                    request,
                    "errors/schema_mismatch.html",
                    {
                        "error_summary": "La base de datos no esta sincronizada con la version actual del sistema.",
                        "requested_path": request.path,
                    },
                    status=503,
                )
                response["Retry-After"] = "120"
                return response
            raise
