from typing import Any

from django.db.models import Q, QuerySet

from apps.influencers.models import ExportReport
from apps.users.models import User


class ReportQueryService:
    """
    Handles ExportReport queryset construction and statistics.

    Keeps report filtering, searching, and ordering out of API views.
    """

    ALLOWED_ORDERING_FIELDS = {
        "created_at": "created_at",
        "-created_at": "-created_at",
        "completed_at": "completed_at",
        "-completed_at": "-completed_at",
        "status": "status",
        "-status": "-status",
        "report_type": "report_type",
        "-report_type": "-report_type",
    }

    @classmethod
    def get_queryset(
        cls,
        user: User,
        filters: Any | None = None,
    ) -> QuerySet[ExportReport]:
        """
        Return the authenticated user's filtered report queryset.

        Supported filters:
            status
            report_type
            search
            ordering

        Invalid ordering values fall back to -created_at.
        """

        queryset = ExportReport.objects.filter(user=user).order_by(
            "-created_at"
        )

        if not filters:
            return queryset

        status_value = filters.get("status")
        report_type = filters.get("report_type")
        search = filters.get("search")
        ordering = filters.get(
            "ordering",
            "-created_at",
        )

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if report_type:
            queryset = queryset.filter(
                report_type=report_type,
            )

        if search:
            queryset = queryset.filter(
                Q(report_type__icontains=search) | Q(status__icontains=search),
            )

        validated_ordering = cls.ALLOWED_ORDERING_FIELDS.get(
            ordering,
            "-created_at",
        )

        return queryset.order_by(
            validated_ordering,
        )

    @staticmethod
    def get_statistics(
        user: User,
    ) -> dict[str, int]:
        """
        Return report statistics for the specified user.
        """

        queryset = ExportReport.objects.filter(
            user=user,
        )

        return {
            "total": queryset.count(),
            "success": queryset.filter(
                status=ExportReport.Status.SUCCESS,
            ).count(),
            "failed": queryset.filter(
                status=ExportReport.Status.FAILED,
            ).count(),
            "processing": queryset.filter(
                status=ExportReport.Status.PROCESSING,
            ).count(),
            "pending": queryset.filter(
                status=ExportReport.Status.PENDING,
            ).count(),
        }
