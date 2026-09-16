import logging
import time

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        start = time.time()

        response = self.get_response(request)

        duration = round(
            (time.time() - start) * 1000,
            2,
        )

        logger.info(
            "API %s %s %sms %s",
            request.method,
            request.path,
            duration,
            response.status_code,
        )

        return response
