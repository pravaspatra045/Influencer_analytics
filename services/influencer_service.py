from apps.users.models import User
from django.db import transaction
from django.utils import timezone
from apps.influencers.models import (
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
    BankDetail,
)
import logging

logger = logging.getLogger(__name__)


class InfluencerService:

    @staticmethod
    @transaction.atomic
    def register_influencer(data):
        """
        Handles complete influencer registration

        Steps:
        1. Create user
        2. Create influencer
        3. Create profile
        4. Create bank details
        5. Create social media accounts

        Uses transaction to ensure atomicity
        """

        try:
            # 🔹 Create user
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                role='influencer'
            )

            # 🔹 Create influencer
            influencer = Influencer.objects.create(user=user)

            # 🔹 Profile
            InfluencerProfile.objects.create(
                influencer=influencer,
                full_name=data['full_name'],
                phone=data['phone']
            )

            # 🔹 Bank details
            BankDetail.objects.create(
                influencer=influencer,
                account_number=data['account_number'],
                bank_name=data['bank_name']
            )

            # 🔹 Social media accounts
            for sm in data['social_media']:
                SocialMediaAccount.objects.create(
                    influencer=influencer,
                    platform=sm['platform'],
                    handle=sm['handle'],
                    followers=sm['followers']
                )

            # Logging success
            logger.info(
                f"Influencer registered successfully | id={influencer.id} | email={user.email}"
            )

            return influencer

        except Exception as e:
            # ❌ Log error with traceback
            logger.error(f"Registration failed | error={str(e)}", exc_info=True)
            raise
        
    @staticmethod
    def update_status(influencer, status, reason=None, updated_by=None):
        """
        Update influencer status with full business rules

        Rules:
        - Only valid transitions allowed
        - Approved/Rejected cannot be modified
        - Rejection requires reason
        - Approval requires all KYC documents verified
        - Audit tracking (approved_by, approved_at)
        """

        valid_status = ['pending', 'on_hold', 'approved', 'rejected']

        # ❌ Invalid status
        if status not in valid_status:
            logger.warning(f"Invalid status | status={status}")
            raise ValueError("Invalid status")

        current_status = influencer.status

        # ❌ Prevent changes after final states
        if current_status in ['approved', 'rejected']:
            logger.warning(
                f"Blocked status change | influencer_id={influencer.id} | current={current_status}"
            )
            raise Exception("Cannot modify approved/rejected influencer")

        # 🔹 Allowed transitions
        allowed_transitions = {
            'pending': ['on_hold', 'approved', 'rejected'],
            'on_hold': ['approved', 'rejected'],
        }

        if status not in allowed_transitions.get(current_status, []):
            logger.warning(
                f"Invalid transition | influencer_id={influencer.id} | {current_status} → {status}"
            )
            raise Exception(f"Invalid status transition from {current_status} to {status}")

        # ❌ Reject must have reason
        if status == 'rejected' and not reason:
            logger.warning(
                f"Rejection without reason | influencer_id={influencer.id}"
            )
            raise ValueError("Rejection reason is required")

        # 🔥 KYC VALIDATION BEFORE APPROVAL
        if status == 'approved':
            documents = influencer.documents.all()

            required_docs = ["pan", "aadhaar", "bank_proof"]

            verified_docs = [
                doc.document_type for doc in documents if doc.is_verified
            ]

            for doc_type in required_docs:
                if doc_type not in verified_docs:
                    logger.warning(
                        f"KYC missing | influencer_id={influencer.id} | missing={doc_type}"
                    )
                    raise Exception(f"{doc_type} document not verified")

        # 🔹 Perform status update
        influencer.status = status

        # 🔹 Handle rejection
        if status == 'rejected':
            influencer.rejection_reason = reason

        # 🔹 Handle approval audit
        if status == 'approved':
            influencer.approved_by = updated_by
            influencer.approved_at = timezone.now()

        #  PROFILE COMPLETION CHECK
        completion = InfluencerService.calculate_profile_completion(influencer)

        if completion < 100:
            logger.warning(
                f"Profile incomplete | influencer_id={influencer.id} | completion={completion}"
            )
            raise Exception("Profile not 100% complete")
        
        influencer.save()

        # ✅ Log success (audit trail)
        logger.info(
            f"Status updated | influencer_id={influencer.id} | "
            f"{current_status} → {status} | by={updated_by}"
        )

        return influencer
    

    @staticmethod
    def calculate_profile_completion(influencer):
        """
        Calculate profile completion percentage
        """

        total_fields = 5
        completed = 0

        # 🔹 Profile
        if hasattr(influencer, "influencerprofile"):
            profile = influencer.influencerprofile

            if profile.full_name:
                completed += 1
            if profile.phone:
                completed += 1

        # 🔹 Bank
        if hasattr(influencer, "bankdetail"):
            bank = influencer.bankdetail

            if bank.account_number:
                completed += 1
            if bank.bank_name:
                completed += 1

        # 🔹 Social media
        if influencer.socialmediaaccount_set.exists():
            completed += 1

        percentage = (completed / total_fields) * 100

        return round(percentage, 2)
