import logging

from celery import shared_task

from apps.influencers.models import ExportReport
from services.export_service import ExportService
from services.report_cleanup_service import ReportCleanupService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
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
    with exponential backoff.

    Report state:
        PENDING
           ↓
        PROCESSING
           ↓
        SUCCESS

    When a generation attempt fails, ExportService marks the report
    as FAILED. If retries remain, this task changes the report back
    to PENDING before scheduling the next attempt.
    """

    logger.info(
        "Started report generation | report_id=%s | task_id=%s | retry=%s",
        report_id,
        self.request.id,
        self.request.retries,
    )

    try:
        report = ExportReport.objects.get(
            id=report_id,
        )
    except ExportReport.DoesNotExist:
        logger.error(
            "Report not found | report_id=%s | task_id=%s",
            report_id,
            self.request.id,
        )

        return {
            "status": "not_found",
            "report_id": report_id,
        }

    if report.status == ExportReport.Status.SUCCESS:
        logger.info(
            "Report already completed | report_id=%s",
            report_id,
        )

        return {
            "status": "already_completed",
            "report_id": report_id,
        }

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

    try:
        ExportService.generate_report(
            report,
        )

        logger.info(
            "Completed report generation | report_id=%s | task_id=%s",
            report_id,
            self.request.id,
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

        if self.request.retries < self.max_retries:
            report.status = ExportReport.Status.PENDING
            report.completed_at = None

            report.save(
                update_fields=(
                    "status",
                    "completed_at",
                ),
            )

            raise self.retry(
                exc=exc,
            )

        logger.error(
            "Report generation permanently failed | "
            "report_id=%s | task_id=%s",
            report_id,
            self.request.id,
        )

        raise


@shared_task
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
