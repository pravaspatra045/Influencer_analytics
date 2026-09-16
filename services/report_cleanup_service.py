import logging
from datetime import timedelta

from django.utils import timezone

from apps.influencers.models import ExportReport

logger = logging.getLogger(__name__)


class ReportCleanupService:
    """Service responsible for cleaning up old export reports."""

    DEFAULT_RETENTION_DAYS = 30

    @classmethod
    def cleanup_old_reports(
        cls,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> int:
        """
        Delete export reports older than the configured retention period.

        Returns:
            Number of reports deleted.
        """
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        deleted_count, _ = ExportReport.objects.filter(
            created_at__lt=cutoff_date,
        ).delete()

        logger.info(
            "Old report cleanup completed | retention_days=%s | deleted=%s",
            retention_days,
            deleted_count,
        )

        return deleted_count
