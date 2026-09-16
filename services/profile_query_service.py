from uuid import UUID

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.influencers.models import Influencer
from apps.users.models import User


class ProfileQueryService:
    """
    Handles database queries related to influencer profiles.
    """

    @staticmethod
    def _base_queryset() -> QuerySet[Influencer]:
        """
        Return the optimized base influencer queryset used by
        profile-related queries.

        Related one-to-one/foreign-key objects are loaded using
        select_related, while reverse collections use prefetch_related.
        """

        return Influencer.objects.select_related(
            "profile",
            "bank_detail",
            "user",
        ).prefetch_related(
            "social_accounts",
        )

    @staticmethod
    def get_my_profile(
        user: User,
    ) -> Influencer:
        """
        Fetch the influencer profile belonging to the authenticated user.

        Raises:
            Http404: If the user does not have an influencer profile.
        """

        return get_object_or_404(
            ProfileQueryService._base_queryset(),
            user=user,
        )

    @staticmethod
    def get_by_influencer_id(
        influencer_id: UUID,
    ) -> Influencer:
        """
        Fetch an influencer using the public influencer UUID.

        Raises:
            Http404: If the influencer does not exist.
        """

        return get_object_or_404(
            ProfileQueryService._base_queryset(),
            influencer_id=influencer_id,
        )
