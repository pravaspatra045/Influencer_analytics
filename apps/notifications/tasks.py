import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone

from apps.notifications.models import BulkNotification, Notification
from services.notification_request import NotificationRequest

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={
        "max_retries": 3,
    },
)
def send_email_notification(
    self,
    notification_id,
    email,
    subject,
    html,
):
    """
    Send notification email.
    """

    notification = Notification.objects.get(notification_id=notification_id)

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
            ]
        )

    except Exception:

        logger.exception("Failed sending email.")

        notification.status = Notification.Status.FAILED

        notification.save(
            update_fields=[
                "status",
            ]
        )

        raise


User = get_user_model()


@shared_task(bind=True)
def process_bulk_notification(self, bulk_notification_id):
    """
    Processes a bulk notification job.
    """
    from services.notification_service import NotificationService

    job = BulkNotification.objects.get(
        bulk_notification_id=bulk_notification_id
    )

    job.status = BulkNotification.Status.PROCESSING
    job.started_at = timezone.now()
    job.save(update_fields=["status", "started_at"])

    try:

        # Determine recipients
        if job.recipient_type == BulkNotification.RecipientType.ALL_USERS:
            users = User.objects.filter(is_active=True)

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
        job.save(update_fields=["total_users"])

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

                NotificationService.send(request)

                processed += 1

            except Exception:
                failed += 1
                logger.exception(
                    "Failed to send notification to user %s",
                    user.id,
                )

            # Update progress every 50 users
            if (processed + failed) % 50 == 0:

                job.processed_users = processed
                job.failed_users = failed

                job.save(
                    update_fields=[
                        "processed_users",
                        "failed_users",
                    ]
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
            ]
        )

    except Exception:

        job.status = BulkNotification.Status.FAILED
        job.completed_at = timezone.now()

        job.save(
            update_fields=[
                "status",
                "completed_at",
            ]
        )

        raise
