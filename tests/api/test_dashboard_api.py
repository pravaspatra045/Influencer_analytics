import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_dashboard_stats(authenticated_client):

    response = authenticated_client.get(reverse("dashboard-stats"))

    assert response.status_code == 200

    assert "total" in response.data["data"]
    assert "approved" in response.data["data"]
    assert "pending" in response.data["data"]
    assert "rejected" in response.data["data"]
    assert "approval_rate" in response.data["data"]


@pytest.mark.django_db
def test_dashboard_requires_authentication(
    api_client,
):

    response = api_client.get(reverse("dashboard-stats"))

    assert response.status_code == 401
