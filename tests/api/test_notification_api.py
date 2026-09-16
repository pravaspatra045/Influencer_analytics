import pytest
from django.urls import reverse

from tests.factories.notification_factory import NotificationFactory
from tests.factories.notification_preference_factory import (
    NotificationPreferenceFactory,
)


@pytest.mark.django_db
def test_list_notifications(
    authenticated_client,
    user,
):

    NotificationFactory.create_batch(
        5,
        user=user,
    )

    response = authenticated_client.get(reverse("notification-list"))

    assert response.status_code == 200

    assert len(response.data["results"]) == 5


@pytest.mark.django_db
def test_notification_list_requires_authentication(
    api_client,
):

    response = api_client.get(reverse("notification-list"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_notification_detail(
    authenticated_client,
    user,
):

    notification = NotificationFactory(
        user=user,
    )

    response = authenticated_client.get(
        reverse(
            "notification-detail",
            kwargs={
                "notification_id": notification.notification_id,
            },
        )
    )

    assert response.status_code == 200

    assert response.data["data"]["title"] == notification.title


@pytest.mark.django_db
def test_mark_notification_read(
    authenticated_client,
    user,
):

    notification = NotificationFactory(
        user=user,
        is_read=False,
    )

    response = authenticated_client.patch(
        reverse(
            "notification-read",
            kwargs={
                "notification_id": notification.notification_id,
            },
        )
    )

    notification.refresh_from_db()

    assert response.status_code == 200

    assert notification.is_read is True


@pytest.mark.django_db
def test_mark_all_notifications_read(
    authenticated_client,
    user,
):

    NotificationFactory.create_batch(
        5,
        user=user,
        is_read=False,
    )

    response = authenticated_client.patch(reverse("notification-read-all"))

    assert response.status_code == 200

    assert (
        NotificationFactory._meta.model.objects.filter(
            user=user,
            is_read=False,
        ).count()
        == 0
    )


@pytest.mark.django_db
def test_delete_notification(
    authenticated_client,
    user,
):

    notification = NotificationFactory(
        user=user,
    )

    response = authenticated_client.delete(
        reverse(
            "notification-delete",
            kwargs={
                "notification_id": notification.notification_id,
            },
        )
    )

    notification.refresh_from_db()

    assert response.status_code == 200

    assert notification.is_deleted is True


@pytest.mark.django_db
def test_unread_count(
    authenticated_client,
    user,
):

    NotificationFactory.create_batch(
        3,
        user=user,
        is_read=False,
    )

    NotificationFactory.create_batch(
        2,
        user=user,
        is_read=True,
    )

    response = authenticated_client.get(reverse("notification-unread-count"))

    assert response.status_code == 200

    assert response.data["data"]["unread_count"] == 3


@pytest.mark.django_db
def test_get_notification_preferences(
    authenticated_client,
    user,
):
    NotificationPreferenceFactory(user=user)

    response = authenticated_client.get(reverse("notification-preferences"))

    assert response.status_code == 200
    assert response.data["message"] == "Preferences fetched successfully."

    data = response.data["data"]

    assert data["registration_email"] is True
    assert data["approval_email"] is True
    assert data["profile_email"] is False


@pytest.mark.django_db
def test_update_notification_preferences(
    authenticated_client,
    user,
):
    preference = NotificationPreferenceFactory(
        user=user,
    )

    payload = {
        "registration_email": False,
        "profile_email": True,
    }

    response = authenticated_client.patch(
        reverse("notification-preferences"),
        payload,
        format="json",
    )

    preference.refresh_from_db()

    assert response.status_code == 200

    assert preference.registration_email is False
    assert preference.profile_email is True


@pytest.mark.django_db
def test_get_preferences_creates_default_preferences(
    authenticated_client,
    user,
):
    response = authenticated_client.get(reverse("notification-preferences"))

    assert response.status_code == 200

    assert response.data["data"]["registration_email"] is True
    assert response.data["data"]["profile_email"] is False
