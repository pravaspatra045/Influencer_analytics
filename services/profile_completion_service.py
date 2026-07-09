from apps.influencers.models import Influencer

class ProfileCompletionService:
    """
    Calculates profile completion.
    """

    PROFILE_WEIGHTS = {
        "full_name": 10,
        "phone": 10,
        "bio": 10,
        "profile_image": 15,
        "date_of_birth": 10,
        "address": 10,
        "bank_details": 15,
        "social_accounts": 10,
        "approved": 10,
    }

    @classmethod
    def calculate(cls, influencer):

        score = 0

        completed = []

        missing = []

        profile = influencer.profile

        # ---------------------------------
        # Full Name
        # ---------------------------------

        if profile.full_name:
            score += cls.PROFILE_WEIGHTS["full_name"]
            completed.append("full_name")
        else:
            missing.append("full_name")

        # ---------------------------------
        # Phone
        # ---------------------------------

        if profile.phone:
            score += cls.PROFILE_WEIGHTS["phone"]
            completed.append("phone")
        else:
            missing.append("phone")

        # ---------------------------------
        # Bio
        # ---------------------------------

        if profile.bio:
            score += cls.PROFILE_WEIGHTS["bio"]
            completed.append("bio")
        else:
            missing.append("bio")

        # ---------------------------------
        # Image
        # ---------------------------------

        if profile.profile_image:
            score += cls.PROFILE_WEIGHTS["profile_image"]
            completed.append("profile_image")
        else:
            missing.append("profile_image")

        # ---------------------------------
        # DOB
        # ---------------------------------

        if profile.date_of_birth:
            score += cls.PROFILE_WEIGHTS["date_of_birth"]
            completed.append("date_of_birth")
        else:
            missing.append("date_of_birth")

        # ---------------------------------
        # Address
        # ---------------------------------

        if (
            profile.city
            and profile.state
            and profile.country
        ):
            score += cls.PROFILE_WEIGHTS["address"]
            completed.append("address")
        else:
            missing.append("address")

        # ---------------------------------
        # Bank
        # ---------------------------------

        if hasattr(influencer, "bank_detail"):

            bank = influencer.bank_detail

            if (
                bank.account_holder_name
                and bank.account_number
                and bank.ifsc_code
            ):
                score += cls.PROFILE_WEIGHTS["bank_details"]
                completed.append("bank_details")
            else:
                missing.append("bank_details")

        else:
            missing.append("bank_details")

        # ---------------------------------
        # Social
        # ---------------------------------

        if influencer.social_accounts.exists():
            score += cls.PROFILE_WEIGHTS["social_accounts"]
            completed.append("social_accounts")
        else:
            missing.append("social_accounts")

        # ---------------------------------
        # Approval
        # ---------------------------------

        if influencer.status == Influencer.Status.APPROVED:
            score += cls.PROFILE_WEIGHTS["approved"]
            completed.append("approved")
        else:
            missing.append("approved")

        return {
            "percentage": score,
            "completed_fields": completed,
            "missing_fields": missing,
        }