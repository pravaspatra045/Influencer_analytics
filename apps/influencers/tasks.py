import logging

from celery import shared_task

from apps.influencers.models import ExportReport
from core.celery_tasks import LoggedTask
from services.export_service import ExportService
from services.report_cleanup_service import ReportCleanupService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    base=LoggedTask,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def generate_influencer_report(
    self,
    report_id: str,
) -> dict[str, str]:
    """
    Generate an influencer report asynchronously.

    Celery retries report-generation failures up to three times
    with exponential backoff and jitter.

    Report state:

        PENDING
           ↓
        PROCESSING
           ↓
        SUCCESS

    On a failed attempt:

        PROCESSING
           ↓
        PENDING
           ↓
        RETRY

    After the final failed attempt, the exception is raised and
    the report remains in the failed state managed by the
    ExportService/report-generation workflow.
    """

    logger.info(
        "Started report generation | " "report_id=%s | task_id=%s | retry=%s",
        report_id,
        self.request.id,
        self.request.retries,
    )

    # ------------------------------------------------------------
    # Fetch report
    # ------------------------------------------------------------
    try:
        report = ExportReport.objects.get(
            id=report_id,
        )

    except ExportReport.DoesNotExist:
        logger.error(
            "Report not found | " "report_id=%s | task_id=%s",
            report_id,
            self.request.id,
        )

        # A missing report is a permanent condition.
        # Do not retry.
        return {
            "status": "not_found",
            "report_id": report_id,
        }

    # ------------------------------------------------------------
    # Idempotency protection
    # ------------------------------------------------------------
    if report.status == ExportReport.Status.SUCCESS:
        logger.info(
            "Report already completed | " "report_id=%s | task_id=%s",
            report_id,
            self.request.id,
        )

        return {
            "status": "already_completed",
            "report_id": report_id,
        }

    # ------------------------------------------------------------
    # Mark report as processing
    # ------------------------------------------------------------
    report.task_id = self.request.id
    report.status = ExportReport.Status.PROCESSING
    report.error_message = None

    report.save(
        update_fields=(
            "task_id",
            "status",
            "error_message",
        ),
    )

    # ------------------------------------------------------------
    # Generate report
    # ------------------------------------------------------------
    try:
        ExportService.generate_report(
            report,
        )

        logger.info(
            "Completed report generation | "
            "report_id=%s | task_id=%s | retry=%s",
            report_id,
            self.request.id,
            self.request.retries,
        )

        return {
            "status": "success",
            "report_id": report_id,
        }

    except Exception as exc:
        logger.exception(
            "Report generation failed | "
            "report_id=%s | task_id=%s | retry=%s",
            report_id,
            self.request.id,
            self.request.retries,
        )

        # --------------------------------------------------------
        # Retry if attempts remain
        # --------------------------------------------------------
        if self.request.retries < self.max_retries:
            report.status = ExportReport.Status.PENDING
            report.completed_at = None

            report.save(
                update_fields=(
                    "status",
                    "completed_at",
                ),
            )

            logger.warning(
                "Scheduling report retry | "
                "report_id=%s | task_id=%s | "
                "retry=%s | max_retries=%s",
                report_id,
                self.request.id,
                self.request.retries + 1,
                self.max_retries,
            )

            raise self.retry(
                exc=exc,
            )

        # --------------------------------------------------------
        # Final failure
        # --------------------------------------------------------
        logger.error(
            "Report generation permanently failed | "
            "report_id=%s | task_id=%s | "
            "retries=%s",
            report_id,
            self.request.id,
            self.request.retries,
        )

        raise


@shared_task(
    base=LoggedTask,
)
def cleanup_old_reports() -> int:
    """
    Delete old report files and database records.
    """

    deleted = ReportCleanupService.cleanup_old_reports()

    logger.info(
        "Report cleanup completed | deleted=%s",
        deleted,
    )

    return deleted
