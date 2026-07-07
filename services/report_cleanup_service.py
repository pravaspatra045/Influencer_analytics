from datetime import timedelta

from django.utils import timezone

from apps.influencers.models import ExportReport


class ReportCleanupService:
    """
    Handles cleanup of old report records and files.
    """

    REPORT_RETENTION_DAYS = 30

    @classmethod
    def cleanup_old_reports(cls):
        """
        Delete reports older than retention period.
        """

        cutoff_date = timezone.now() - timedelta(
            days=cls.REPORT_RETENTION_DAYS
        )

        reports = ExportReport.objects.filter(
            completed_at__lt=cutoff_date
        )

        deleted = 0

        for report in reports:

            if report.file:
                report.file.delete(save=False)

            report.delete()

            deleted += 1

        return deleted