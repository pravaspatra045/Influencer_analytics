import logging

from django.core.cache import cache
from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Liveness check.

    Confirms that the Django application process is running.
    Does not check external dependencies.
    """
    return JsonResponse(
        {
            "status": "ok",
            "service": "influencer-platform",
        },
        status=200,
    )


def readiness_check(request):
    """
    Readiness check.

    Verifies that Django can communicate with its critical
    infrastructure dependencies.
    """
    checks = {
        "database": False,
        "redis": False,
    }

    # Database check
    try:
        connection.ensure_connection()
        checks["database"] = True
    except OperationalError:
        logger.exception("Readiness check failed: database unavailable")

    # Redis/cache check
    try:
        cache.set("health_check", "ok", timeout=10)
        checks["redis"] = cache.get("health_check") == "ok"
    except Exception:
        logger.exception("Readiness check failed: Redis unavailable")

    is_ready = all(checks.values())

    return JsonResponse(
        {
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
        },
        status=200 if is_ready else 503,
    )
