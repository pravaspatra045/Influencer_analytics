from django.shortcuts import get_object_or_404

from apps.influencers.models import Influencer


class ProfileQueryService:
    """
    Handles all profile-related database queries.
    """

    @staticmethod
    def get_my_profile(user):
        """
        Fetch the authenticated user's influencer profile.
        """

        return get_object_or_404(
            Influencer.objects.select_related(
                "profile",
                "bank_detail",
                "user",
            ).prefetch_related(
                "social_accounts",
            ),
            user=user,
        )

    @staticmethod
    def get_by_influencer_id(influencer_id):
        """
        Fetch influencer by public influencer_id.
        """

        return get_object_or_404(
            Influencer.objects.select_related(
                "profile",
                "bank_detail",
                "user",
            ).prefetch_related(
                "social_accounts",
            ),
            influencer_id=influencer_id,
        )