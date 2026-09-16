from unittest.mock import patch

import pytest

from apps.notifications.models import Notification
from services.notification_request import NotificationRequest
from services.notification_service import NotificationService
from tests.factories.notification_factory import NotificationFactory
from tests.factories.user_factory import UserFactory


@pytest.mark.django_db
@patch("services.notification_service.NotificationPreferenceService.can_send")
def test_send_returns_none_when_preferences_disabled(mock_can_send):

    mock_can_send.return_value = False

    user = UserFactory()

    request = NotificationRequest(
        user=user,
        title="Welcome",
        message="Hello",
        category=Notification.Category.SYSTEM,
        notification_type=Notification.Type.IN_APP,
    )

    result = NotificationService.send(request)

    assert result is None

    assert Notification.objects.count() == 0

    mock_can_send.assert_called_once()


@pytest.mark.django_db
@patch("services.notification_service.NotificationPreferenceService.can_send")
def test_send_creates_in_app_notification(mock_can_send):
    """
    In-app notification should be created and marked as SENT.
    """

    mock_can_send.return_value = True

    user = UserFactory()

    request = NotificationRequest(
        user=user,
        title="Welcome",
        message="Hello User",
        category=Notification.Category.SYSTEM,
        notification_type=Notification.Type.IN_APP,
        payload={"foo": "bar"},
    )

    notification = NotificationService.send(request)

    assert notification is not None

    assert Notification.objects.count() == 1

    notification.refresh_from_db()

    assert notification.user == user
    assert notification.title == "Welcome"
    assert notification.message == "Hello User"
    assert notification.payload == {"foo": "bar"}

    assert notification.status == Notification.Status.SENT


@pytest.mark.django_db
@patch("services.notification_service.send_email_notification.delay")
@patch("services.notification_service.NotificationTemplateService.render")
@patch("services.notification_service.NotificationPreferenceService.can_send")
def test_send_email_notification(
    mock_can_send,
    mock_render,
    mock_delay,
):
    """
    Email notification should create a Notification,
    render the template and queue a Celery task.
    """

    mock_can_send.return_value = True
    mock_render.return_value = "<h1>Hello</h1>"

    user = UserFactory()

    request = NotificationRequest(
        user=user,
        title="Welcome",
        message="Welcome to our platform",
        category=Notification.Category.SYSTEM,
        notification_type=Notification.Type.EMAIL,
        template="welcome_email.html",
        subject="Welcome",
        context={
            "name": "John",
        },
    )

    notification = NotificationService.send(request)

    assert notification is not None

    notification.refresh_from_db()

    assert notification.user == user
    assert notification.title == "Welcome"
    assert notification.notification_type == Notification.Type.EMAIL

    mock_render.assert_called_once_with(
        template_name="welcome_email.html",
        context={"name": "John"},
    )

    mock_delay.assert_called_once()

    kwargs = mock_delay.call_args.kwargs

    assert kwargs["email"] == user.email
    assert kwargs["subject"] == "Welcome"
    assert kwargs["html"] == "<h1>Hello</h1>"
    assert kwargs["notification_id"] == str(notification.notification_id)


@pytest.mark.django_db
def test_mark_as_read():

    notification = NotificationFactory(
        is_read=False,
        read_at=None,
    )

    NotificationService.mark_as_read(notification)

    notification.refresh_from_db()

    assert notification.is_read is True

    assert notification.read_at is not None


@pytest.mark.django_db
def test_mark_as_read_does_not_change_read_notification():

    notification = NotificationFactory(
        is_read=True,
    )

    original_read_at = notification.read_at

    NotificationService.mark_as_read(notification)

    notification.refresh_from_db()

    assert notification.is_read is True

    assert notification.read_at == original_read_at


@pytest.mark.django_db
def test_mark_all_as_read():

    user = UserFactory()

    unread1 = NotificationFactory(
        user=user,
        is_read=False,
    )

    unread2 = NotificationFactory(
        user=user,
        is_read=False,
    )

    already_read = NotificationFactory(
        user=user,
        is_read=True,
    )

    NotificationService.mark_all_as_read(user)

    unread1.refresh_from_db()
    unread2.refresh_from_db()
    already_read.refresh_from_db()

    assert unread1.is_read is True
    assert unread2.is_read is True
    assert already_read.is_read is True

    assert unread1.read_at is not None
    assert unread2.read_at is not None


@pytest.mark.django_db
def test_mark_all_as_read_only_affects_current_user():

    user1 = UserFactory()

    user2 = UserFactory()

    user1_notification = NotificationFactory(
        user=user1,
        is_read=False,
    )

    user2_notification = NotificationFactory(
        user=user2,
        is_read=False,
    )

    NotificationService.mark_all_as_read(user1)

    user1_notification.refresh_from_db()

    user2_notification.refresh_from_db()

    assert user1_notification.is_read is True

    assert user2_notification.is_read is False


@pytest.mark.django_db
def test_delete_notification():

    notification = NotificationFactory(
        is_deleted=False,
        deleted_at=None,
    )

    NotificationService.delete(notification)

    notification.refresh_from_db()

    assert notification.is_deleted is True

    assert notification.deleted_at is not None
