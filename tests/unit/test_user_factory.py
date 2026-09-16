import pytest

from tests.factories.user_factory import UserFactory


@pytest.mark.django_db
def test_user_factory():

    user = UserFactory()

    assert user.username.startswith("user")

    assert user.email.endswith("@example.com")

    assert user.role == "influencer"

    assert user.check_password("Password@123")
