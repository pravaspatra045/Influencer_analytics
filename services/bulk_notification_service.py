from apps.notifications.models import BulkNotification
from apps.notifications.tasks import process_bulk_notification


class BulkNotificationService:
    """
    Handles bulk notification business logic.
    """

    @staticmethod
    def create_job(
        *,
        created_by,
        title,
        message,
        category,
        notification_type,
        recipient_type,
        template=None,
        subject=None,
        payload=None,
    ):
        """
        Creates a bulk notification job.
        """

        job = BulkNotification.objects.create(
            created_by=created_by,
            title=title,
            message=message,
            category=category,
            notification_type=notification_type,
            recipient_type=recipient_type,
            template=template,
            subject=subject,
            payload=payload or {},
        )

        task = process_bulk_notification.delay(str(job.bulk_notification_id))

        job.task_id = task.id

        job.save(
            update_fields=[
                "task_id",
            ]
        )

        return job
