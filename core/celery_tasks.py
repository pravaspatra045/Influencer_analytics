import logging
import time

from celery import Task

logger = logging.getLogger(__name__)


class LoggedTask(Task):
    """
    Base Celery task with production-oriented logging.

    Logs:
    - task name
    - task ID
    - execution duration
    - success
    - failure
    - retry attempts
    """

    autoretry_for = ()
    retry_backoff = True
    retry_backoff_max = 300
    retry_jitter = True
    max_retries = 3

    def __call__(self, *args, **kwargs):
        start_time = time.perf_counter()

        logger.info(
            "Celery task started | task=%s task_id=%s retry=%s",
            self.name,
            self.request.id,
            self.request.retries,
        )

        try:
            result = super().__call__(*args, **kwargs)

            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.info(
                "Celery task succeeded | "
                "task=%s task_id=%s retry=%s duration_ms=%s",
                self.name,
                self.request.id,
                self.request.retries,
                duration_ms,
            )

            return result

        except Exception:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.exception(
                "Celery task failed | "
                "task=%s task_id=%s retry=%s duration_ms=%s",
                self.name,
                self.request.id,
                self.request.retries,
                duration_ms,
            )

            raise
