import logging
import smtplib

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from apps.notifications.models import BulkNotification, Notification
from core.celery_tasks import LoggedTask
from services.notification_request import NotificationRequest

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(
    bind=True,
    base=LoggedTask,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def send_email_notification(
    self,
    notification_id,
    email,
    subject,
    html,
):
    """
    Send notification email asynchronously.

    Retry behavior:
        - retries transient SMTP failures up to 3 times
        - uses exponential backoff with jitter
        - does not retry missing Notification records
        - marks the notification as FAILED only after
          the final attempt fails
    """

    logger.info(
        "Started email notification | "
        "notification_id=%s | email=%s | task_id=%s | retry=%s",
        notification_id,
        email,
        self.request.id,
        self.request.retries,
    )

    try:
        notification = Notification.objects.get(
            notification_id=notification_id,
        )

    except Notification.DoesNotExist:
        logger.error(
            "Notification not found | " "notification_id=%s | task_id=%s",
            notification_id,
            self.request.id,
        )

        return {
            "status": "not_found",
            "notification_id": str(notification_id),
        }

    # Idempotency protection.
    #
    # If the notification has already been successfully sent,
    # do not send it again.
    if notification.status == Notification.Status.SENT:
        logger.info(
            "Notification already sent | " "notification_id=%s | task_id=%s",
            notification_id,
            self.request.id,
        )

        return {
            "status": "already_sent",
            "notification_id": str(notification_id),
        }

    try:
        email_message = EmailMultiAlternatives(
            subject=subject,
            body="",
            to=[email],
        )

        email_message.attach_alternative(
            html,
            "text/html",
        )

        email_message.send()

        notification.status = Notification.Status.SENT

        notification.save(
            update_fields=[
                "status",
            ],
        )

        logger.info(
            "Email notification sent | "
            "notification_id=%s | task_id=%s | retry=%s",
            notification_id,
            self.request.id,
            self.request.retries,
        )

        return {
            "status": "sent",
            "notification_id": str(notification_id),
        }

    except smtplib.SMTPException as exc:
        logger.exception(
            "SMTP error while sending notification | "
            "notification_id=%s | task_id=%s | retry=%s",
            notification_id,
            self.request.id,
            self.request.retries,
        )

        if self.request.retries < self.max_retries:
            logger.warning(
                "Scheduling email notification retry | "
                "notification_id=%s | task_id=%s | "
                "retry=%s | max_retries=%s",
                notification_id,
                self.request.id,
                self.request.retries + 1,
                self.max_retries,
            )

            raise self.retry(
                exc=exc,
            )

        notification.status = Notification.Status.FAILED

        notification.save(
            update_fields=[
                "status",
            ],
        )

        logger.error(
            "Email notification permanently failed | "
            "notification_id=%s | task_id=%s | retries=%s",
            notification_id,
            self.request.id,
            self.request.retries,
        )

        raise

    except Exception:
        # Non-SMTP errors are treated as application/data errors.
        # Do not automatically retry these.
        logger.exception(
            "Unexpected error while sending notification | "
            "notification_id=%s | task_id=%s | retry=%s",
            notification_id,
            self.request.id,
            self.request.retries,
        )

        notification.status = Notification.Status.FAILED

        notification.save(
            update_fields=[
                "status",
            ],
        )

        raise


@shared_task(
    bind=True,
    base=LoggedTask,
)
def process_bulk_notification(
    self,
    bulk_notification_id,
):
    """
    Process a bulk notification job.

    Individual recipient failures are isolated so one failed
    notification does not stop the complete bulk operation.

    The complete task is intentionally NOT automatically retried,
    because retrying the entire job could resend notifications
    to users that already received them.
    """

    from services.notification_service import NotificationService

    logger.info(
        "Started bulk notification | " "bulk_notification_id=%s | task_id=%s",
        bulk_notification_id,
        self.request.id,
    )

    try:
        job = BulkNotification.objects.get(
            bulk_notification_id=bulk_notification_id,
        )

    except BulkNotification.DoesNotExist:
        logger.error(
            "Bulk notification job not found | "
            "bulk_notification_id=%s | task_id=%s",
            bulk_notification_id,
            self.request.id,
        )

        return {
            "status": "not_found",
            "bulk_notification_id": str(bulk_notification_id),
        }

    job.status = BulkNotification.Status.PROCESSING
    job.started_at = timezone.now()

    job.save(
        update_fields=[
            "status",
            "started_at",
        ],
    )

    try:
        # Determine recipients.
        if job.recipient_type == BulkNotification.RecipientType.ALL_USERS:
            users = User.objects.filter(
                is_active=True,
            )

        elif (
            job.recipient_type
            == BulkNotification.RecipientType.ALL_INFLUENCERS
        ):
            users = User.objects.filter(
                is_active=True,
                role="INFLUENCER",
            )

        else:
            users = User.objects.none()

        total_users = users.count()

        job.total_users = total_users

        job.save(
            update_fields=[
                "total_users",
            ],
        )

        processed = 0
        failed = 0

        for user in users.iterator():

            try:
                request = NotificationRequest(
                    user=user,
                    title=job.title,
                    message=job.message,
                    category=job.category,
                    notification_type=job.notification_type,
                    template=job.template,
                    subject=job.subject,
                    payload=job.payload,
                )

                NotificationService.send(
                    request,
                )

                processed += 1

            except Exception:
                failed += 1

                logger.exception(
                    "Failed to send bulk notification | "
                    "bulk_notification_id=%s | user_id=%s | "
                    "task_id=%s",
                    bulk_notification_id,
                    user.id,
                    self.request.id,
                )

            # Update progress every 50 users.
            if (processed + failed) % 50 == 0:
                job.processed_users = processed
                job.failed_users = failed

                job.save(
                    update_fields=[
                        "processed_users",
                        "failed_users",
                    ],
                )

        job.processed_users = processed
        job.failed_users = failed
        job.status = BulkNotification.Status.COMPLETED
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "processed_users",
                "failed_users",
                "status",
                "completed_at",
            ],
        )

        logger.info(
            "Bulk notification completed | "
            "bulk_notification_id=%s | task_id=%s | "
            "total=%s | processed=%s | failed=%s",
            bulk_notification_id,
            self.request.id,
            total_users,
            processed,
            failed,
        )

        return {
            "status": "completed",
            "bulk_notification_id": str(bulk_notification_id),
            "total_users": total_users,
            "processed_users": processed,
            "failed_users": failed,
        }

    except Exception:
        job.status = BulkNotification.Status.FAILED
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "completed_at",
            ],
        )

        logger.exception(
            "Bulk notification permanently failed | "
            "bulk_notification_id=%s | task_id=%s",
            bulk_notification_id,
            self.request.id,
        )

        raise
