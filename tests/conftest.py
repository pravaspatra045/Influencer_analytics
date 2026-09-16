import pytest
from rest_framework.test import APIClient

from apps.influencers.models import Influencer
from tests.factories.user_factory import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def admin_user():
    return UserFactory(role="ADMIN")


@pytest.fixture
def influencer_user():
    return UserFactory(role="INFLUENCER")


@pytest.fixture
def authenticated_client(api_client, influencer_user):
    api_client.force_authenticate(user=influencer_user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def influencer(influencer_user):
    return Influencer.objects.create(
        user=influencer_user,
        status=Influencer.Status.PENDING,
    )
