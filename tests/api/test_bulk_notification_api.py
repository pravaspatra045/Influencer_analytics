import uuid

import pytest
from django.urls import reverse

from apps.notifications.models import BulkNotification
from tests.factories.bulk_notification_factory import BulkNotificationFactory
from tests.factories.user_factory import UserFactory


@pytest.mark.django_db
def test_create_bulk_notification(admin_client):

    payload = {
        "title": "System Maintenance",
        "message": "Application will be unavailable tonight.",
        "category": "SYSTEM",
        "notification_type": "IN_APP",
        "recipient_type": "ALL_USERS",
    }

    response = admin_client.post(
        reverse("bulk-notification-create"),
        payload,
        format="json",
    )

    assert response.status_code == 201

    assert BulkNotification.objects.count() == 1

    job = BulkNotification.objects.first()

    assert job.title == payload["title"]
    assert job.message == payload["message"]


@pytest.mark.django_db
def test_create_bulk_notification_validation_error(
    authenticated_client,
):

    payload = {
        "title": "",
    }

    response = authenticated_client.post(
        reverse("bulk-notification-create"),
        payload,
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_list_bulk_notifications(
    authenticated_client,
    influencer_user,
):
    BulkNotificationFactory.create_batch(
        3,
        created_by=influencer_user,
    )

    response = authenticated_client.get(reverse("bulk-notification-list"))

    assert response.status_code == 200

    assert len(response.data["results"]) == 3


@pytest.mark.django_db
def test_bulk_notification_detail(
    authenticated_client,
    influencer_user,
):
    job = BulkNotificationFactory(
        created_by=influencer_user,
    )

    response = authenticated_client.get(
        reverse(
            "bulk-notification-detail",
            kwargs={
                "bulk_notification_id": job.bulk_notification_id,
            },
        )
    )

    assert response.status_code == 200

    assert response.data["title"] == job.title


@pytest.mark.django_db
def test_bulk_notification_requires_authentication(
    api_client,
):

    response = api_client.get(reverse("bulk-notification-list"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_bulk_notification_queryset_returns_only_current_users_jobs(
    authenticated_client,
    influencer_user,
):

    BulkNotificationFactory.create_batch(
        2,
        created_by=influencer_user,
    )

    other_user = UserFactory()

    BulkNotificationFactory.create_batch(
        4,
        created_by=other_user,
    )

    response = authenticated_client.get(reverse("bulk-notification-list"))

    assert response.status_code == 200

    assert len(response.data["results"]) == 2


@pytest.mark.django_db
def test_bulk_notification_invalid_uuid(
    authenticated_client,
):

    response = authenticated_client.get(
        reverse(
            "bulk-notification-detail",
            kwargs={
                "bulk_notification_id": uuid.uuid4(),
            },
        )
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_bulk_notification_response_fields(
    authenticated_client,
    user,
):

    job = BulkNotificationFactory(
        created_by=user,
    )

    response = authenticated_client.get(
        reverse(
            "bulk-notification-detail",
            kwargs={
                "bulk_notification_id": job.bulk_notification_id,
            },
        )
    )

    assert response.status_code == 200

    data = response.data

    assert "title" in data
    assert "message" in data
    assert "status" in data
    assert "progress" in data
    assert "processed_users" in data
    assert "failed_users" in data
