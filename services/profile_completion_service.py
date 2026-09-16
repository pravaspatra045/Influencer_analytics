from apps.influencers.models import Influencer


class ProfileCompletionService:
    """Calculate influencer profile completion percentage."""

    TOTAL_FIELDS = 4

    @staticmethod
    def calculate(influencer: Influencer) -> int:
        completed_fields = 0

        if getattr(influencer, "profile", None):
            completed_fields += 1

        if getattr(influencer, "bank_detail", None):
            completed_fields += 1

        if influencer.social_accounts.exists():
            completed_fields += 1

        if influencer.documents.exists():
            completed_fields += 1

        return int(
            (completed_fields / ProfileCompletionService.TOTAL_FIELDS) * 100,
        )
