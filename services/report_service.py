from typing import Any

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.influencers.models import ExportReport
from apps.users.models import User
from services.export_service import ExportService
from services.influencer_query_service import InfluencerQueryService
from services.report_dispatcher import ReportDispatcher
from services.report_query_service import ReportQueryService


class ReportServiceError(Exception):
    """Base exception for report service errors."""


class InvalidExportFormatError(ReportServiceError):
    """Raised when an unsupported export format is requested."""


class ReportRetryError(ReportServiceError):
    """Raised when a report cannot be retried."""


class ReportService:
    """
    Handles report generation, retrieval, export, retry,
    and report statistics.

    Responsibilities are intentionally separated:

        ReportService
            ↓
        ReportQueryService  → report database queries
        ReportDispatcher    → asynchronous report execution
        ExportService       → CSV/Excel generation
        InfluencerQueryService → influencer filtering
    """

    EXPORT_FORMATS = {
        "csv": {
            "filename": "influencers.csv",
            "content_type": "text/csv",
        },
        "excel": {
            "filename": "influencers.xlsx",
            "content_type": (
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        },
    }

    @staticmethod
    def get_reports(
        user: User,
        params: Any,
    ):
        """
        Return reports belonging to the specified user.

        Filtering and queryset construction remain delegated to
        ReportQueryService.
        """

        return ReportQueryService.get_queryset(
            user=user,
            filters=params,
        )

    @staticmethod
    def get_report_for_download(
        report_id,
        user: User,
    ) -> ExportReport:
        """
        Fetch a report and verify that the requesting user owns it.

        Raises:
            Http404: If the report does not exist.
            PermissionDenied: If another user owns the report.
        """

        report = get_object_or_404(
            ExportReport,
            id=report_id,
        )

        if report.user_id != user.id:
            raise PermissionDenied(
                "You are not allowed to access this report.",
            )

        return report

    @staticmethod
    def create_export_report(
        user: User,
        filters: dict[str, Any] | None = None,
        report_type: str = "INFLUENCER_EXPORT",
    ) -> ExportReport:
        """
        Create a pending export report and dispatch it for processing.
        """

        report = ExportReport.objects.create(
            user=user,
            report_type=report_type,
            filters=filters or {},
            status=ExportReport.Status.PENDING,
        )

        ReportDispatcher.dispatch(report)

        return report

    @staticmethod
    def export_report(
        filters: dict[str, Any],
        export_format: str,
    ) -> dict[str, Any]:
        """
        Generate an influencer export.

        Supported formats:
            csv
            excel

        Returns:
            Dictionary containing:
                buffer
                filename
                content_type

        Raises:
            InvalidExportFormatError: If the requested format is unsupported.
        """

        export_config = ReportService.EXPORT_FORMATS.get(
            export_format,
        )

        if export_config is None:
            raise InvalidExportFormatError(
                "Invalid export format.",
            )

        queryset = InfluencerQueryService.get_queryset(
            filters,
        )

        if export_format == "csv":
            buffer = ExportService.generate_csv(
                queryset,
            )
        else:
            buffer = ExportService.generate_excel(
                queryset,
            )

        return {
            "buffer": buffer,
            "filename": export_config["filename"],
            "content_type": export_config["content_type"],
        }

    @staticmethod
    def retry_report(
        report_id,
        user: User,
    ) -> ExportReport:
        """
        Retry a failed report.

        Only the report owner can retry it.
        Only reports in FAILED state can be retried.
        """

        report = get_object_or_404(
            ExportReport,
            id=report_id,
            user=user,
        )

        if report.status != ExportReport.Status.FAILED:
            raise ReportRetryError(
                "Only failed reports can be retried.",
            )

        report.status = ExportReport.Status.PENDING
        report.error_message = None
        report.completed_at = None

        report.save(
            update_fields=(
                "status",
                "error_message",
                "completed_at",
            ),
        )

        ReportDispatcher.retry(
            report,
        )

        return report

    @staticmethod
    def get_report_statistics(
        user: User,
    ) -> dict[str, Any]:
        """
        Return report statistics for the specified user.
        """

        return ReportQueryService.get_statistics(
            user,
        )
