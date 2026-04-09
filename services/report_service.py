import csv
from io import StringIO, BytesIO
from openpyxl import Workbook


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