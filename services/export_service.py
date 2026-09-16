import csv
import logging
import tempfile
from io import BytesIO, StringIO
from uuid import uuid4

from django.utils import timezone
from openpyxl import Workbook

from apps.influencers.exports import generate_influencer_excel
from apps.influencers.models import ExportReport
from services.influencer_query_service import InfluencerQueryService
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


class ExportServiceError(Exception):
    """Base exception for export-service errors."""


class ReportGenerationError(ExportServiceError):
    """Raised when report generation fails."""


class ExportService:
    """
    Handles CSV, Excel, and asynchronous report generation.
    """

    CSV_HEADERS = (
        "ID",
        "Email",
        "Status",
        "Created At",
        "Approved At",
    )

    EXCEL_SHEET_NAME = "Influencers"

    @staticmethod
    def generate_csv(queryset) -> StringIO:
        """
        Generate a CSV export from the supplied queryset.

        The queryset is expected to contain the required related
        user information.
        """

        buffer = StringIO()
        writer = csv.writer(buffer)

        writer.writerow(ExportService.CSV_HEADERS)

        for influencer in queryset:
            writer.writerow(
                (
                    influencer.id,
                    influencer.user.email,
                    influencer.status,
                    influencer.created_at,
                    influencer.approved_at,
                ),
            )

        buffer.seek(0)

        return buffer

    @staticmethod
    def generate_excel(queryset) -> BytesIO:
        """
        Generate an Excel export from the supplied queryset.
        """

        workbook = Workbook()
        worksheet = workbook.active

        if worksheet is None:
            raise ReportGenerationError(
                "Unable to create Excel worksheet.",
            )

        worksheet.title = ExportService.EXCEL_SHEET_NAME

        worksheet.append(
            list(ExportService.CSV_HEADERS),
        )

        for influencer in queryset:
            worksheet.append(
                [
                    influencer.id,
                    influencer.user.email,
                    influencer.status,
                    influencer.created_at,
                    influencer.approved_at,
                ],
            )

        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        return buffer

    @staticmethod
    def generate_report(
        report: ExportReport,
    ) -> None:
        """
        Generate and store an asynchronous Excel report.

        On success:
            - report file is stored
            - status becomes SUCCESS
            - completed_at is populated

        On failure:
            - status becomes FAILED
            - error_message is populated
            - exception is re-raised for the caller/task to handle

        The Excel file is generated inside a temporary directory so
        StorageService can move it into the configured Django storage
        without risking deletion of the final stored report.
        """

        try:
            queryset = InfluencerQueryService.get_queryset(
                report.filters,
            )

            filename = f"influencer_report_{uuid4().hex}.xlsx"

            with tempfile.TemporaryDirectory(
                prefix="influencer-report-",
            ) as temp_directory:
                file_path = generate_influencer_excel(
                    queryset=queryset,
                    filename=filename,
                    output_directory=temp_directory,
                )

                StorageService.save_report_file(
                    report,
                    file_path,
                )

            report.status = ExportReport.Status.SUCCESS
            report.completed_at = timezone.now()
            report.error_message = None

            report.save(
                update_fields=(
                    "status",
                    "completed_at",
                    "error_message",
                ),
            )

            logger.info(
                "Report generated successfully | report_id=%s",
                report.id,
            )

        except Exception as exc:
            logger.exception(
                "Report generation failed | report_id=%s",
                report.id,
            )

            report.status = ExportReport.Status.FAILED
            report.error_message = str(exc)
            report.completed_at = None

            report.save(
                update_fields=(
                    "status",
                    "error_message",
                    "completed_at",
                ),
            )

            raise ReportGenerationError(
                "Report generation failed.",
            ) from exc
