from celery import shared_task
from services.report_service import ReportService
from services.storage_service import StorageService
from apps.influencers.models import Influencer
from apps.influencers.models import Report
import datetime


@shared_task(bind=True)
def generate_influencer_report(self, report_id):

    report = Report.objects.get(id=report_id)

    try:
        report.status = "processing"
        report.save()

        queryset = Influencer.objects.select_related("user").all()

        buffer = ReportService.generate_excel(queryset)

        filename = f"reports/report_{report.id}.xlsx"

        url = StorageService.upload_file(buffer, filename)

        report.status = "completed"
        report.file_url = url
        report.save()

    except Exception as e:
        report.status = "failed"
        report.error_message = str(e)
        report.save()

        raise