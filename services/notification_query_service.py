from django.shortcuts import get_object_or_404

from apps.notifications.models import Notification


class NotificationQueryService:
    """
    Handles notification database queries.
    """

    @staticmethod
    def get_queryset(user, filters=None):
        queryset = Notification.objects.filter(
            user=user,
            is_deleted=False,
        )

        filters = filters or {}

        if filters.get("is_read") is not None:
            queryset = queryset.filter(is_read=filters["is_read"])

        if filters.get("category"):
            queryset = queryset.filter(category=filters["category"])

        if filters.get("notification_type"):
            queryset = queryset.filter(
                notification_type=filters["notification_type"]
            )

        if filters.get("search"):
            queryset = queryset.filter(title__icontains=filters["search"])

        ordering = filters.get(
            "ordering",
            "-created_at",
        )

        return queryset.order_by(ordering)

    @staticmethod
    def get_notification(notification_id, user):
        """
        Returns a single notification.
        """

        return get_object_or_404(
            Notification,
            notification_id=notification_id,
            user=user,
            is_deleted=False,
        )

    @staticmethod
    def unread_count(user):
        """
        Returns unread notification count.
        """

        return Notification.objects.filter(
            user=user,
            is_read=False,
            is_deleted=False,
        )
