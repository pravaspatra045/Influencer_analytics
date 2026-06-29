import logging
import os
from uuid import uuid4

from celery import shared_task
from django.core.files import File
from django.utils import timezone

from apps.influencers.exports import generate_influencer_excel
from apps.influencers.models import ExportReport, Influencer

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_influencer_report(self, report_id):
    """
    Generate influencer report in background.
    """

    logger.info(f"Started report generation : {report_id}")

    report = ExportReport.objects.get(id=report_id)

    report.task_id = self.request.id
    report.status = ExportReport.Status.PROCESSING
    report.save(update_fields=["task_id", "status"])

    try:

        influencers = Influencer.objects.select_related("user").all()

        filename = f"influencer_report_{uuid4().hex}.xlsx"

        file_path = generate_influencer_excel(
            influencers=influencers,
            filename=filename,
        )

        with open(file_path, "rb") as excel_file:
            report.file.save(
                filename,
                File(excel_file),
                save=False,
            )

        report.status = ExportReport.Status.SUCCESS
        report.completed_at = timezone.now()

        report.save()

        if os.path.exists(file_path):
            os.remove(file_path)

        logger.info(f"Completed report generation : {report_id}")

    except Exception as e:

        logger.exception("Report generation failed")

        report.status = ExportReport.Status.FAILED
        report.error_message = str(e)
        report.completed_at = timezone.now()

        report.save()

        raise