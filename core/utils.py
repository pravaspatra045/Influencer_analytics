from datetime import timedelta
from typing import Any

from django.utils import timezone


def standard_response(
    message: str = "",
    error: Any = None,
    data: Any = None,
    status: int = 200,
) -> dict[str, Any]:
    """
    Return the standard API response format.

    :param message: Success or informational message.
    :param error: Error details, if any.
    :param data: Response payload.
    :param status: HTTP status code.
    """

    return {
        "message": message,
        "error": error,
        "data": data,
        "status": status,
    }


def get_date_range(
    range_param: str | None,
):
    """
    Return the start datetime for a supported date range.

    Supported values:
        7d  -> last 7 days
        30d -> last 30 days
        90d -> last 90 days

    Returns None for unsupported or missing values.
    """

    now = timezone.now()

    range_days = {
        "7d": 7,
        "30d": 30,
        "90d": 90,
    }

    days = range_days.get(range_param)

    if days is None:
        return None

    return now - timedelta(days=days)
