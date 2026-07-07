from django.db.models import Q
from django.db.models import Count
from apps.influencers.models import ExportReport



class ReportQueryService:
    """
    Handles all ExportReport queryset logic.
    """

    @staticmethod
    def get_queryset(user, filters=None):
        """
        Returns filtered report queryset.
        """

        queryset = ExportReport.objects.filter(
            user=user
        )

        if not filters:
            return queryset.order_by("-created_at")

        status = filters.get("status")
        report_type = filters.get("report_type")
        search = filters.get("search")
        ordering = filters.get(
            "ordering",
            "-created_at",
        )

        if status:
            queryset = queryset.filter(
                status=status
            )

        if report_type:
            queryset = queryset.filter(
                report_type=report_type
            )

        if search:
            queryset = queryset.filter(
                Q(report_type__icontains=search)
                |
                Q(status__icontains=search)
            )

        return queryset.order_by(ordering)
    

    @staticmethod
    def get_statistics(user):
        """
        Returns report statistics for the user.
        """

        queryset = ExportReport.objects.filter(user=user)

        return {
            "total": queryset.count(),
            "success": queryset.filter(
                status=ExportReport.Status.SUCCESS
            ).count(),
            "failed": queryset.filter(
                status=ExportReport.Status.FAILED
            ).count(),
            "processing": queryset.filter(
                status=ExportReport.Status.PROCESSING
            ).count(),
            "pending": queryset.filter(
                status=ExportReport.Status.PENDING
            ).count(),
        }