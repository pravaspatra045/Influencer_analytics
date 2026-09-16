from typing import Any

from django.db import transaction

from apps.influencers.models import (
    BankDetail,
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
)


class ProfileService:
    """
    Handles influencer profile business logic.

    Profile updates are performed atomically so that profile,
    bank, and social-media changes either all succeed or all
    roll back.
    """

    @staticmethod
    @transaction.atomic
    def update_profile(
        influencer: Influencer,
        profile_data: dict[str, Any],
        bank_data: dict[str, Any] | None = None,
        social_accounts: list[dict[str, Any]] | None = None,
    ) -> Influencer:
        """
        Update influencer profile, bank details, and social accounts.

        Social-account behavior:
            - Existing platforms are updated.
            - New platforms are created.
            - Existing platforms omitted from the submitted list
              are deleted.

        All changes occur inside a single database transaction.
        """

        ProfileService._update_profile(
            influencer.profile,
            profile_data,
        )

        if bank_data:
            bank = ProfileService._get_or_create_bank_detail(
                influencer,
            )
            ProfileService._update_bank_detail(
                bank,
                bank_data,
            )

        if social_accounts is not None:
            ProfileService._update_social_accounts(
                influencer,
                social_accounts,
            )

        return influencer

    @staticmethod
    def _update_profile(
        profile: InfluencerProfile,
        profile_data: dict[str, Any],
    ) -> None:
        """
        Update supplied influencer profile fields.
        """

        if not profile_data:
            return

        changed_fields = []

        for field, value in profile_data.items():
            setattr(profile, field, value)
            changed_fields.append(field)

        if changed_fields:
            profile.save(
                update_fields=changed_fields,
            )

    @staticmethod
    def _get_or_create_bank_detail(
        influencer: Influencer,
    ) -> BankDetail:
        """
        Return the influencer's bank details, creating them if necessary.
        """

        bank_detail, _ = BankDetail.objects.get_or_create(
            influencer=influencer,
        )

        return bank_detail

    @staticmethod
    def _update_bank_detail(
        bank_detail: BankDetail,
        bank_data: dict[str, Any],
    ) -> None:
        """
        Update supplied bank-detail fields.
        """

        changed_fields = []

        for field, value in bank_data.items():
            setattr(bank_detail, field, value)
            changed_fields.append(field)

        if changed_fields:
            bank_detail.save(
                update_fields=changed_fields,
            )

    @staticmethod
    def _update_social_accounts(
        influencer: Influencer,
        social_accounts: list[dict[str, Any]],
    ) -> None:
        """
        Synchronize the influencer's social-media accounts.

        Existing accounts are updated by platform.
        New platforms are inserted.
        Platforms omitted from the request are deleted.
        """

        existing_accounts = {
            account.platform: account
            for account in influencer.social_accounts.all()
        }

        incoming_platforms = {
            account_data["platform"] for account_data in social_accounts
        }

        accounts_to_create = []

        for account_data in social_accounts:
            platform = account_data["platform"]
            existing_account = existing_accounts.get(platform)

            if existing_account is None:
                accounts_to_create.append(
                    SocialMediaAccount(
                        influencer=influencer,
                        **account_data,
                    ),
                )
                continue

            changed_fields = []

            for field, value in account_data.items():
                setattr(
                    existing_account,
                    field,
                    value,
                )
                changed_fields.append(field)

            if changed_fields:
                existing_account.save(
                    update_fields=changed_fields,
                )

        if accounts_to_create:
            SocialMediaAccount.objects.bulk_create(
                accounts_to_create,
            )

        (
            SocialMediaAccount.objects.filter(influencer=influencer)
            .exclude(platform__in=incoming_platforms)
            .delete()
        )
