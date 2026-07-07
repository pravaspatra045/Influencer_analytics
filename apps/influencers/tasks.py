import logging
import os
from uuid import uuid4

from celery import shared_task
from django.core.files import File
from django.utils import timezone

from apps.influencers.exports import generate_influencer_excel
from apps.influencers.models import ExportReport

logger = logging.getLogger(__name__)
from services.report_cleanup_service import (ReportCleanupService)

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_influencer_report(self, report_id):
    """
    Background task for generating reports.
    """

    logger.info(
        "Started report generation : %s",
        report_id
    )

    report = ExportReport.objects.get(
        id=report_id
    )

    report.task_id = self.request.id
    report.status = ExportReport.Status.PROCESSING

    report.save(
        update_fields=[
            "task_id",
            "status",
        ]
    )

    try:

        from services.export_service import ExportService

        ExportService.generate_report(report)

        logger.info(
            "Completed report generation : %s",
            report_id,
        )

    except Exception as exc:

        logger.exception(
            "Report generation failed"
        )

        report.status = ExportReport.Status.FAILED
        report.error_message = str(exc)
        report.completed_at = timezone.now()

        report.save()

        raise
    
@shared_task
def cleanup_old_reports():
    """
    Delete old report files and database records.
    """

    deleted = (
        ReportCleanupService.cleanup_old_reports()
    )

    logger.info(
        "Cleanup completed. Deleted %s reports.",
        deleted,
    )

    return deleted