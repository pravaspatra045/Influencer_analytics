from django.db.models import QuerySet

from apps.influencers.models import Influencer


class InfluencerQueryService:
    """
    Shared service for building influencer querysets.

    Every API that needs influencer filtering
    should use this service.

    This avoids duplicate ORM logic.
    """

    @staticmethod
    def get_queryset(filters=None) -> QuerySet:
        """
        Returns filtered queryset.
        """

        queryset = (
            Influencer.objects
            .select_related("user")
            .all()
        )

        if not filters:
            return queryset

        status = filters.get("status")
        search = filters.get("search")
        ordering = filters.get("ordering")
        min_followers = filters.get("min_followers")
        max_followers = filters.get("max_followers")

        if status:
            queryset = queryset.filter(status=status)

        if search:
            queryset = queryset.filter(
                full_name__icontains=search
            )

        if min_followers:
            queryset = queryset.filter(
                followers__gte=min_followers
            )

        if max_followers:
            queryset = queryset.filter(
                followers__lte=max_followers
            )

        if ordering:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by("-created_at")

        return queryset