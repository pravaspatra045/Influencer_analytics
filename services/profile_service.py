from django.db import transaction

from apps.influencers.models import (
    BankDetail,
    InfluencerProfile,
    SocialMediaAccount,
)
from services.storage_service import StorageService


class ProfileService:
    """
    Handles all profile-related business logic.
    """

    @staticmethod
    @transaction.atomic
    def update_profile(
        influencer,
        profile_data,
        bank_data=None,
        social_accounts=None,
    ):
        """
        Update influencer profile, bank details and social accounts.
        """

        profile = influencer.profile

        # -----------------------------
        # Update profile
        # -----------------------------
        for field, value in profile_data.items():
            setattr(profile, field, value)

        profile.save()

        # -----------------------------
        # Update bank details
        # -----------------------------
        if bank_data:

            bank, _ = BankDetail.objects.get_or_create(
                influencer=influencer
            )

            for field, value in bank_data.items():
                setattr(bank, field, value)

            bank.save()

        # -----------------------------
        # Update social accounts
        # -----------------------------
        if social_accounts is not None:

            existing_accounts = {
                account.platform: account
                for account in SocialMediaAccount.objects.filter(
                    influencer=influencer
                )
            }

            incoming_platforms = set()

            for account_data in social_accounts:

                platform = account_data["platform"]
                incoming_platforms.add(platform)

                if platform in existing_accounts:

                    social_account = existing_accounts[platform]

                    for field, value in account_data.items():
                        setattr(
                            social_account,
                            field,
                            value,
                        )

                    social_account.save()

                else:

                    SocialMediaAccount.objects.create(
                        influencer=influencer,
                        **account_data,
                    )

            SocialMediaAccount.objects.filter(
                influencer=influencer
            ).exclude(
                platform__in=incoming_platforms
            ).delete()

        return influencer
    
    