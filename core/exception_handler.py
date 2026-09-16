from rest_framework.views import exception_handler

from core.utils import standard_response


def custom_exception_handler(exc, context):
    """
    Global DRF Exception Handler

    Every API exception will pass through here.
    """

    response = exception_handler(exc, context)

    if response is None:
        return response

    response.data = standard_response(
        message="Request failed.",
        error=response.data,
        status=response.status_code,
    )

    return response
