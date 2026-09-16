import pytest
from django.urls import reverse

from tests.factories.user_factory import UserFactory


@pytest.mark.django_db
def test_login_success(api_client):

    password = "Password@123"

    user = UserFactory()

    user.set_password(password)

    user.save()

    url = reverse("login")

    response = api_client.post(
        url,
        {
            "email": user.email,
            "password": password,
        },
        format="json",
    )

    assert response.status_code == 200

    assert response.data["message"] == "Login successful"

    assert "access" in response.data["data"]

    assert "refresh" in response.data["data"]

    assert response.data["data"]["role"] == user.role


@pytest.mark.django_db
def test_login_invalid_password(
    api_client,
):

    user = UserFactory()

    user.set_password("Password@123")

    user.save()

    url = reverse("login")

    response = api_client.post(
        url,
        {
            "email": user.email,
            "password": "WrongPassword",
        },
        format="json",
    )

    assert response.status_code == 400

    assert response.data["message"] == "Login failed"


@pytest.mark.django_db
def test_login_unknown_email(
    api_client,
):

    url = reverse("login")

    response = api_client.post(
        url,
        {
            "email": "unknown@test.com",
            "password": "Password@123",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_without_password(
    api_client,
):

    url = reverse("login")

    response = api_client.post(
        url,
        {
            "email": "abc@test.com",
        },
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_login_without_email(
    api_client,
):

    url = reverse("login")

    response = api_client.post(
        url,
        {
            "password": "Password@123",
        },
        format="json",
    )

    assert response.status_code == 400
