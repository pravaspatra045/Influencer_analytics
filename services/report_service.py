import csv
from io import StringIO, BytesIO
from openpyxl import Workbook
from apps.influencers.models import ExportReport
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from apps.influencers.tasks import generate_influencer_report


class ReportService:
    """
    Handles CSV & Excel export logic
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
    def get_reports(user):

        return (
            ExportReport.objects
            .filter(user=user)
            .order_by("-created_at")
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

        task = generate_influencer_report.delay(
            str(report.id)
        )

        report.task_id = task.id

        report.save(update_fields=["task_id"])

        return report