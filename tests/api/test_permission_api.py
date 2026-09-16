import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_notification_requires_login(api_client):

    response = api_client.get(reverse("notification-list"))

    assert response.status_code == 401


@pytest.mark.django_db
def test_my_profile_requires_login(api_client):

    response = api_client.get(reverse("my-profile"))

    assert response.status_code == 401


@pytest.mark.parametrize(
    "url_name",
    [
        "dashboard-stats",
        "dashboard-trend",
        "growth-rate",
        "rejection-rate",
        "status-distribution",
    ],
)
@pytest.mark.django_db
def test_dashboard_requires_login(
    api_client,
    url_name,
):

    response = api_client.get(reverse(url_name))

    assert response.status_code == 401
