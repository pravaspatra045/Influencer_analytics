import factory
from factory.django import DjangoModelFactory

from apps.influencers.models import (
    BankDetail,
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
)
from tests.factories.user_factory import UserFactory


class InfluencerFactory(DjangoModelFactory):
    """
    Factory for Influencer model.
    """

    class Meta:
        model = Influencer

    user = factory.SubFactory(UserFactory)

    status = "pending"

    referral_code = factory.Sequence(lambda n: f"REF{1000+n}")

    rejection_reason = None

    approved_by = None

    approved_at = None


class InfluencerProfileFactory(DjangoModelFactory):
    """
    Factory for InfluencerProfile.
    """

    class Meta:
        model = InfluencerProfile

    influencer = factory.SubFactory(InfluencerFactory)

    full_name = factory.Faker("name")

    phone = factory.Sequence(lambda n: f"987654{1000+n}")

    bio = factory.Faker("paragraph")

    city = factory.Faker("city")

    state = factory.Faker("state")

    country = "India"

    pincode = factory.Sequence(lambda n: f"{751000+n}")


class SocialMediaAccountFactory(DjangoModelFactory):
    """
    Factory for SocialMediaAccount.
    """

    class Meta:
        model = SocialMediaAccount

    influencer = factory.SubFactory(InfluencerFactory)

    platform = "INSTAGRAM"

    handle = factory.Sequence(lambda n: f"influencer_{n}")

    profile_url = factory.LazyAttribute(
        lambda obj: f"https://instagram.com/{obj.handle}"
    )

    followers = factory.Faker(
        "random_int",
        min=100,
        max=1000000,
    )

    is_verified = False


class BankDetailFactory(DjangoModelFactory):
    """
    Factory for BankDetail.
    """

    class Meta:
        model = BankDetail

    influencer = factory.SubFactory(InfluencerFactory)

    account_holder_name = factory.Faker("name")

    account_number = factory.Sequence(lambda n: f"123456789{n}")

    bank_name = factory.Faker("company")

    ifsc_code = factory.Sequence(lambda n: f"SBIN000{n:04d}")

    upi_id = factory.Sequence(lambda n: f"user{n}@upi")

    is_verified = False
