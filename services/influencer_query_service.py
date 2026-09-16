from typing import Any

from django.db.models import Q, QuerySet

from apps.influencers.models import Influencer


class InfluencerQueryService:
    """
    Centralized queryset builder for influencer-related queries.

    Keeps filtering, searching, ordering, and query optimization
    out of API views.
    """

    ALLOWED_ORDERING_FIELDS = {
        "created_at": "created_at",
        "-created_at": "-created_at",
        "approved_at": "approved_at",
        "-approved_at": "-approved_at",
        "status": "status",
        "-status": "-status",
        "influencer_id": "influencer_id",
        "-influencer_id": "-influencer_id",
    }

    @classmethod
    def get_queryset(
        cls,
        filters: dict[str, Any] | None = None,
    ) -> QuerySet[Influencer]:
        """
        Build and return an optimized influencer queryset.

        Supported filters:
            status
            search
            ordering
            min_followers
            max_followers
        """

        queryset = (
            Influencer.objects.select_related(
                "user",
                "profile",
                "bank_detail",
            )
            .prefetch_related(
                "social_accounts",
                "documents",
            )
            .all()
        )

        if not filters:
            return queryset.order_by("-created_at")

        status_value = filters.get("status")
        search = filters.get("search")
        ordering = filters.get("ordering")
        min_followers = filters.get("min_followers")
        max_followers = filters.get("max_followers")

        if status_value:
            queryset = queryset.filter(
                status=status_value,
            )

        if search:
            queryset = queryset.filter(
                Q(profile__full_name__icontains=search)
                | Q(user__username__icontains=search)
                | Q(user__email__icontains=search)
                | Q(influencer_id__icontains=search)
            )

        if min_followers is not None:
            queryset = queryset.filter(
                social_accounts__followers__gte=min_followers,
            )

        if max_followers is not None:
            queryset = queryset.filter(
                social_accounts__followers__lte=max_followers,
            )

        if ordering:
            validated_ordering = cls.ALLOWED_ORDERING_FIELDS.get(
                ordering,
            )

            if validated_ordering:
                queryset = queryset.order_by(
                    validated_ordering,
                )
            else:
                queryset = queryset.order_by(
                    "-created_at",
                )
        else:
            queryset = queryset.order_by(
                "-created_at",
            )

        return queryset.distinct()
