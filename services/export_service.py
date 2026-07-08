import logging
import os
from uuid import uuid4

from django.core.files import File
from django.utils import timezone

from apps.influencers.exports import generate_influencer_excel
from apps.influencers.models import ExportReport
from services.influencer_query_service import InfluencerQueryService
from services.storage_service import StorageService
import csv
from io import StringIO, BytesIO
from openpyxl import Workbook

logger = logging.getLogger(__name__)


class ExportService:
    """
    Handles report export generation.
    """

    @staticmethod
    def generate_csv(queryset):
        """
        Generate CSV from queryset
        """

        buffer = StringIO()
        writer = csv.writer(buffer)

        # Header
        writer.writerow([
            "ID", "Email", "Status", "Created At", "Approved At"
        ])

        # Rows
        for obj in queryset:
            writer.writerow([
                obj.id,
                obj.user.email,
                obj.status,
                obj.created_at,
                obj.approved_at
            ])

        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_excel(queryset):
        """
        Generate Excel file
        """

        wb = Workbook()
        ws = wb.active
        ws.title = "Influencers"

        # Header
        ws.append([
            "ID", "Email", "Status", "Created At", "Approved At"
        ])

        # Rows
        for obj in queryset:
            ws.append([
                obj.id,
                obj.user.email,
                obj.status,
                obj.created_at,
                obj.approved_at
            ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return buffer
    
    @staticmethod
    def generate_report(report: ExportReport):
        """
        Generate excel report and update report status.
        """

        queryset = InfluencerQueryService.get_queryset(
            report.filters
        )

        filename = f"influencer_report_{uuid4().hex}.xlsx"

        file_path = generate_influencer_excel(
            queryset=queryset,
            filename=filename,
        )

        StorageService.save_report_file(
            report,
            file_path,
        )

        report.status = ExportReport.Status.SUCCESS
        report.completed_at = timezone.now()

        report.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

        StorageService.delete_local_file(file_path)

        logger.info(
            "Report %s generated successfully.",
            report.id
        )