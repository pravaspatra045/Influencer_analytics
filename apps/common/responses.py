from rest_framework.response import Response


def standard_response(message="", error=None, data=None, status=200):
    """
    Standard API response format.
    """
    return Response(
        {
            "message": message,
            "error": error,
            "data": data,
            "status": status,
        },
        status=status,
    )