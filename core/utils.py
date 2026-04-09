def standard_response(message="", error=None, data=None, status=200):
    """
    Standard API response format used across all endpoints

    :param message: success or info message
    :param error: error details (if any)
    :param data: response payload
    :param status: HTTP status code
    """
    return {
        "message": message,
        "error": error,
        "data": data,
        "status": status
    }
    
from datetime import timedelta
from django.utils import timezone


def get_date_range(range_param):
    """
    Returns start_date based on range
    """
    now = timezone.now()

    if range_param == "7d":
        return now - timedelta(days=7)
    elif range_param == "30d":
        return now - timedelta(days=30)
    elif range_param == "90d":
        return now - timedelta(days=90)

    return None