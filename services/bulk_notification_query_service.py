from django.shortcuts import get_object_or_404

from apps.notifications.models import BulkNotification


class BulkNotificationQueryService:
    """
    Handles BulkNotification database queries.
    """

    @staticmethod
    def get_queryset(user):
        """
        Returns all bulk notification jobs
        created by the current user.
        """

        return BulkNotification.objects.filter(created_by=user).order_by(
            "-created_at"
        )

    @staticmethod
    def get_job(bulk_notification_id, user):
        """
        Returns a single bulk notification job.
        """

        return get_object_or_404(
            BulkNotification,
            bulk_notification_id=bulk_notification_id,
            created_by=user,
        )
