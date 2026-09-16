import logging
from typing import Iterable

from django.db import transaction
from django.utils import timezone

from apps.notifications.models import Notification
from apps.users.models import User
from services.notification_request import NotificationRequest
from services.notification_template_service import NotificationTemplateService

logger = logging.getLogger(__name__)


class NotificationServiceError(Exception):
    """Base exception for notification service errors."""


class NotificationService:
    """
    Handles notification business logic.
    """

    @staticmethod
    @transaction.atomic
    def send(
        request: NotificationRequest,
    ) -> Notification:
        """
        Create and dispatch a notification.
        """

        notification = Notification.objects.create(
            user=request.user,
            title=request.title,
            message=request.message,
            category=request.category,
            notification_type=request.notification_type,
            payload=request.payload or {},
            status=Notification.Status.PENDING,
        )

        logger.info(
            "Notification created | notification_id=%s | user_id=%s | type=%s",
            notification.notification_id,
            request.user.id,
            request.notification_type,
        )

        if request.notification_type == Notification.Type.EMAIL:
            transaction.on_commit(
                lambda: NotificationService._send_email(
                    notification,
                    request,
                ),
            )

        elif request.notification_type == Notification.Type.IN_APP:
            notification.status = Notification.Status.SENT

            notification.save(
                update_fields=("status",),
            )

        return notification

    @staticmethod
    def _send_email(
        notification: Notification,
        request: NotificationRequest,
    ) -> None:
        """
        Queue email notification after the database transaction commits.
        """

        from apps.notifications.tasks import send_email_notification

        html = NotificationTemplateService.render(
            template_name=request.template,
            context=request.context or {},
        )

        send_email_notification.delay(
            str(notification.notification_id),
            request.user.email,
            request.subject or request.title,
            html,
        )

    @staticmethod
    @transaction.atomic
    def mark_as_read(
        notification: Notification,
    ) -> Notification:
        """
        Mark a notification as read.
        """

        if notification.is_read:
            return notification

        notification.is_read = True
        notification.read_at = timezone.now()

        notification.save(
            update_fields=(
                "is_read",
                "read_at",
            ),
        )

        logger.info(
            "Notification marked as read | notification_id=%s",
            notification.notification_id,
        )

        return notification

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(
        user: User,
    ) -> int:
        """
        Mark all unread notifications as read.
        """

        updated = Notification.objects.filter(
            user=user,
            is_read=False,
            is_deleted=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),
        )

        logger.info(
            "All notifications marked read | user_id=%s | count=%s",
            user.id,
            updated,
        )

        return updated

    @staticmethod
    @transaction.atomic
    def delete(
        notification: Notification,
    ) -> None:
        """
        Soft delete a notification.
        """

        if notification.is_deleted:
            return

        notification.is_deleted = True
        notification.deleted_at = timezone.now()

        notification.save(
            update_fields=(
                "is_deleted",
                "deleted_at",
            ),
        )

        logger.info(
            "Notification deleted | notification_id=%s",
            notification.notification_id,
        )

    @staticmethod
    @transaction.atomic
    def bulk_create(
        users: Iterable[User],
        title: str,
        message: str,
        category: str = Notification.Category.SYSTEM,
        notification_type: str = Notification.Type.IN_APP,
    ) -> int:
        """
        Create in-app notifications for multiple users.
        """

        notifications = [
            Notification(
                user=user,
                title=title,
                message=message,
                category=category,
                notification_type=notification_type,
                status=Notification.Status.SENT,
            )
            for user in users
        ]

        if not notifications:
            return 0

        Notification.objects.bulk_create(
            notifications,
        )

        logger.info(
            "Bulk notifications created | count=%s | category=%s",
            len(notifications),
            category,
        )

        return len(notifications)
