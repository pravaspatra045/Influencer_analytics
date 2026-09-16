from typing import Any

from apps.influencers.models import ExportReport
from apps.influencers.tasks import generate_influencer_report


class ReportDispatcher:
    """
    Responsible for dispatching report-generation background tasks.

    This class keeps Celery-specific dispatching outside the
    report business logic.
    """

    @staticmethod
    def dispatch(
        report: ExportReport,
    ) -> Any:
        """
        Queue a report-generation task.

        The generated Celery task ID is stored against the report
        so the task can be tracked later.
        """

        task = generate_influencer_report.delay(
            str(report.id),
        )

        report.task_id = task.id

        report.save(
            update_fields=("task_id",),
        )

        return task

    @staticmethod
    def retry(
        report: ExportReport,
    ) -> Any:
        """
        Re-dispatch an existing report for processing.

        The report is expected to have already been reset to
        PENDING by ReportService.
        """

        return ReportDispatcher.dispatch(
            report,
        )
