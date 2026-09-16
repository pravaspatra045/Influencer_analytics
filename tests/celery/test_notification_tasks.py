from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model

from apps.notifications.models import BulkNotification, Notification
from apps.notifications.tasks import (
    process_bulk_notification,
    send_email_notification,
)
from tests.factories.bulk_notification_factory import BulkNotificationFactory
from tests.factories.notification_factory import NotificationFactory
from tests.factories.user_factory import UserFactory

User = get_user_model()


@pytest.mark.django_db
@patch("apps.notifications.tasks.EmailMultiAlternatives")
def test_send_email_notification_success(mock_email):

    notification = NotificationFactory(status=Notification.Status.PENDING)

    email_instance = MagicMock()
    mock_email.return_value = email_instance

    send_email_notification(
        notification_id=str(notification.notification_id),
        email="test@example.com",
        subject="Welcome",
        html="<h1>Hello</h1>",
    )

    notification.refresh_from_db()

    mock_email.assert_called_once_with(
        subject="Welcome",
        body="",
        to=["test@example.com"],
    )

    email_instance.attach_alternative.assert_called_once_with(
        "<h1>Hello</h1>",
        "text/html",
    )

    email_instance.send.assert_called_once()

    assert notification.status == Notification.Status.SENT


@pytest.mark.django_db
@patch("apps.notifications.tasks.EmailMultiAlternatives")
def test_send_email_notification_failure(mock_email):

    notification = NotificationFactory(status=Notification.Status.PENDING)

    email_instance = MagicMock()

    email_instance.send.side_effect = Exception("SMTP Error")

    mock_email.return_value = email_instance

    with pytest.raises(Exception):

        send_email_notification(
            notification_id=str(notification.notification_id),
            email="test@example.com",
            subject="Welcome",
            html="<h1>Hello</h1>",
        )

    notification.refresh_from_db()

    assert notification.status == Notification.Status.FAILED


# Test bulk notification all users
@pytest.mark.django_db
@patch("services.notification_service.NotificationService.send")
def test_process_bulk_notification_all_users(
    mock_send,
):

    UserFactory.create_batch(5)

    job = BulkNotificationFactory()

    assert job.status == BulkNotification.Status.PENDING
    assert job.started_at is None
    assert job.completed_at is None

    process_bulk_notification(
        bulk_notification_id=str(job.bulk_notification_id)
    )

    job.refresh_from_db()

    assert job.status == BulkNotification.Status.COMPLETED

    assert job.started_at is not None

    assert job.completed_at is not None

    assert job.total_users == 5

    assert job.processed_users == 5

    assert job.failed_users == 0

    assert mock_send.call_count == 5


@pytest.mark.django_db
@patch("services.notification_service.NotificationService.send")
def test_process_bulk_notification_only_influencers(
    mock_send,
):

    UserFactory(role="ADMIN")

    UserFactory(role="MANAGER")

    UserFactory.create_batch(
        3,
        role="INFLUENCER",
    )

    job = BulkNotificationFactory(
        recipient_type=BulkNotification.RecipientType.ALL_INFLUENCERS
    )

    process_bulk_notification(
        bulk_notification_id=str(job.bulk_notification_id)
    )

    job.refresh_from_db()

    assert job.total_users == 3

    assert job.processed_users == 3

    assert mock_send.call_count == 3


@pytest.mark.django_db
@patch("services.notification_service.NotificationService.send")
def test_bulk_notification_no_users(
    mock_send,
):

    job = BulkNotificationFactory(recipient_type="UNKNOWN")

    process_bulk_notification(
        bulk_notification_id=str(job.bulk_notification_id)
    )

    job.refresh_from_db()

    assert job.total_users == 0

    assert job.processed_users == 0

    assert job.failed_users == 0

    assert job.status == BulkNotification.Status.COMPLETED

    mock_send.assert_not_called()


@pytest.mark.django_db
@patch("services.notification_service.NotificationService.send")
def test_process_bulk_notification_partial_failure(
    mock_send,
):

    UserFactory.create_batch(5)

    mock_send.side_effect = [
        None,
        None,
        Exception("SMTP Error"),
        None,
        Exception("Redis Error"),
    ]

    job = BulkNotificationFactory()

    process_bulk_notification(
        bulk_notification_id=str(job.bulk_notification_id)
    )

    job.refresh_from_db()

    assert job.status == BulkNotification.Status.COMPLETED

    assert job.processed_users == 3

    assert job.failed_users == 2


@pytest.mark.django_db
@patch("apps.notifications.tasks.BulkNotification.objects.get")
def test_bulk_notification_job_failure(
    mock_get,
):

    mock_get.side_effect = Exception("Database Error")

    with pytest.raises(Exception):

        process_bulk_notification(bulk_notification_id="123")


@pytest.mark.django_db
@patch("services.notification_service.NotificationService.send")
@patch("apps.notifications.models.BulkNotification.save")
def test_progress_saved_every_50_users(
    mock_save,
    mock_send,
):

    UserFactory.create_batch(120)

    job = BulkNotificationFactory()

    process_bulk_notification(
        bulk_notification_id=str(job.bulk_notification_id)
    )

    # Initial save:
    # PROCESSING

    # Save total_users

    # Progress at 50

    # Progress at 100

    # Final COMPLETED

    assert mock_save.call_count >= 5
