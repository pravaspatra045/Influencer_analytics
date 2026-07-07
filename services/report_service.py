from apps.influencers.models import ExportReport
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from services.export_service import ExportService
from services.influencer_query_service import InfluencerQueryService
from services.report_query_service import (
    ReportQueryService,
)
from services.report_dispatcher import ReportDispatcher

class ReportService:
    """
    Handles CSV & Excel export logic
    """

    
    @staticmethod
    def get_reports(user, params):
        """
        Returns report queryset.
        """

        return ReportQueryService.get_queryset(
            user=user,
            filters=params,
        )
        
    @staticmethod
    def get_report_for_download(report_id, user):

        report = get_object_or_404(
            ExportReport,
            id=report_id
        )

        if report.user != user:
            raise PermissionDenied(
                "You are not allowed to access this report."
            )

        return report
    
    @staticmethod
    def create_export_report(
        user,
        filters=None,
        report_type="INFLUENCER_EXPORT",
    ):

        report = ExportReport.objects.create(
            user=user,
            report_type=report_type,
            filters=filters or {},
            status=ExportReport.Status.PENDING,
        )

        ReportDispatcher.dispatch(report)

        return report
    
    
    @staticmethod
    def export_report(filters, export_format):
        """
        Returns export file buffer and metadata.
        """

        queryset = InfluencerQueryService.get_queryset(filters)

        if export_format == "csv":

            return {
                "buffer": ExportService.generate_csv(queryset),
                "filename": "influencers.csv",
                "content_type": "text/csv",
            }

        elif export_format == "excel":

            return {
                "buffer": ExportService.generate_excel(queryset),
                "filename": "influencers.xlsx",
                "content_type": (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ),
            }

        raise ValueError("Invalid export format.")
    
    @staticmethod
    def retry_report(report_id, user):
        """
        Retry a failed report.

        Only the owner of the report can retry it.
        Only reports with FAILED status are allowed.
        """

        report = get_object_or_404(
            ExportReport,
            id=report_id,
            user=user,
        )

        if report.status != ExportReport.Status.FAILED:
            raise ValueError(
                "Only failed reports can be retried."
            )

        # Reset report state
        report.status = ExportReport.Status.PENDING
        report.error_message = None
        report.completed_at = None

        report.save(
            update_fields=[
                "status",
                "error_message",
                "completed_at",
            ]
        )

        # Queue the report again
        ReportDispatcher.retry(report)

        return report
    
    @staticmethod
    def get_report_statistics(user):
        """
        Returns report statistics.
        """

        return ReportQueryService.get_statistics(user)