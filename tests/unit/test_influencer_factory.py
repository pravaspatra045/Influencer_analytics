import pytest

from tests.factories.influencer_factory import (
    BankDetailFactory,
    InfluencerFactory,
    InfluencerProfileFactory,
    SocialMediaAccountFactory,
)


@pytest.mark.django_db
def test_influencer_factory():

    influencer = InfluencerFactory()

    assert influencer.user is not None
    assert influencer.status == "pending"


@pytest.mark.django_db
def test_profile_factory():

    profile = InfluencerProfileFactory()

    assert profile.influencer is not None
    assert profile.full_name


@pytest.mark.django_db
def test_social_factory():

    account = SocialMediaAccountFactory()

    assert account.platform == "INSTAGRAM"
    assert account.handle.startswith("influencer_")


@pytest.mark.django_db
def test_bank_factory():

    bank = BankDetailFactory()

    assert bank.account_number
    assert bank.bank_name
