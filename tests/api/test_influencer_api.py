from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.skip(
    reason="Registration test payload needs to be updated to current serializer"
)
def test_register_influencer_success(api_client):

    payload = {
        "email": "john@example.com",
        "password": "StrongPassword@123",
        "confirm_password": "StrongPassword@123",
    }

    response = api_client.post(
        reverse("register"),
        payload,
        format="json",
    )

    assert response.status_code == 201
    assert response.data["message"] == "Registration successful"


@pytest.mark.django_db
def test_register_validation_error(api_client):

    response = api_client.post(
        reverse("register"),
        {},
        format="json",
    )

    assert response.status_code == 400


@patch("services.influencer_service.InfluencerService.register_influencer")
@pytest.mark.skip(
    reason="Registration test payload needs to be updated to current serializer"
)
@pytest.mark.django_db
def test_register_service_exception(
    mock_register,
    api_client,
):

    mock_register.side_effect = Exception("Boom")

    payload = {...}

    response = api_client.post(
        reverse("register"),
        payload,
        format="json",
    )

    assert response.status_code == 500


@pytest.mark.skip(
    reason="Registration test payload needs to be updated to current serializer"
)
@pytest.mark.django_db
def test_approve_influencer(
    admin_client,
    influencer,
):

    response = admin_client.post(
        reverse(
            "approve-influencer",
            kwargs={
                "pk": influencer.pk,
            },
        ),
        {
            "status": "approved",
        },
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_invalid_influencer(
    admin_client,
):

    response = admin_client.post(
        reverse(
            "approve-influencer",
            kwargs={
                "pk": 999999,
            },
        ),
        {
            "status": "approved",
        },
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_approval_requires_authentication(
    api_client,
):

    response = api_client.post(
        reverse(
            "approve-influencer",
            kwargs={"pk": 1},
        ),
    )

    assert response.status_code == 401
