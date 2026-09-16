import logging
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.influencers.models import (
    BankDetail,
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
)
from apps.notifications.models import Notification
from apps.users.models import User
from services.notification_request import NotificationRequest
from services.notification_service import NotificationService

logger = logging.getLogger(__name__)


class InfluencerServiceError(Exception):
    """Base exception for influencer service errors."""


class InvalidInfluencerStatusError(InfluencerServiceError):
    """Raised when an invalid influencer status is supplied."""


class InvalidStatusTransitionError(InfluencerServiceError):
    """Raised when an invalid influencer status transition is attempted."""


class FinalStatusModificationError(InfluencerServiceError):
    """Raised when a final influencer status is modified."""


class RejectionReasonRequiredError(InfluencerServiceError):
    """Raised when rejection is attempted without a reason."""


class KYCVerificationError(InfluencerServiceError):
    """Raised when required KYC documents are not verified."""


class ProfileIncompleteError(InfluencerServiceError):
    """Raised when an influencer profile is incomplete."""


class InfluencerService:
    """
    Service layer for influencer registration and status management.

    Business logic is kept here rather than inside API views.
    """

    @staticmethod
    @transaction.atomic
    def register_influencer(data: dict[str, Any]) -> Influencer:
        """
        Register an influencer and all related records atomically.

        Creates:
            1. User
            2. Influencer
            3. Influencer profile
            4. Bank details
            5. Social media accounts

        The registration notification is sent only after the
        database transaction successfully commits.
        """

        try:
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password"],
                role=User.Role.INFLUENCER,
            )

            influencer = Influencer.objects.create(
                user=user,
            )

            InfluencerProfile.objects.create(
                influencer=influencer,
                full_name=data["full_name"],
                phone=data["phone"],
            )

            BankDetail.objects.create(
                influencer=influencer,
                account_number=data["account_number"],
                bank_name=data["bank_name"],
            )

            SocialMediaAccount.objects.bulk_create(
                [
                    SocialMediaAccount(
                        influencer=influencer,
                        platform=social_media["platform"],
                        handle=social_media["handle"],
                        followers=social_media["followers"],
                    )
                    for social_media in data["social_media"]
                ]
            )

            notification_request = NotificationRequest(
                user=user,
                title="Registration Successful",
                message=("Your registration has been submitted successfully."),
                category=Notification.Category.REGISTRATION,
                notification_type=Notification.Type.EMAIL,
                template="welcome",
                subject="Welcome to Influencer Analytics",
                context={
                    "username": user.username,
                },
                payload={
                    "influencer_id": str(influencer.influencer_id),
                },
            )

            transaction.on_commit(
                lambda: NotificationService.send(
                    notification_request,
                ),
            )

            logger.info(
                "Influencer registered successfully | id=%s | email=%s",
                influencer.id,
                user.email,
            )

            return influencer

        except Exception:
            logger.exception(
                "Influencer registration failed | username=%s | email=%s",
                data.get("username"),
                data.get("email"),
            )
            raise

    @staticmethod
    @transaction.atomic
    def update_status(
        influencer: Influencer,
        status: str,
        reason: str | None = None,
        updated_by: User | None = None,
    ) -> Influencer:
        """
        Update influencer status according to business rules.

        Rules:
            - Only supported statuses are allowed.
            - Approved/rejected influencers cannot be modified.
            - Only defined status transitions are allowed.
            - Rejection requires a reason.
            - Approval requires all required KYC documents to be verified.
            - Approval records approver and approval timestamp.
            - Approval/rejection notifications are sent after commit.
            - Profile must be 100% complete before approval.
        """

        valid_statuses = {
            Influencer.Status.PENDING,
            Influencer.Status.ON_HOLD,
            Influencer.Status.APPROVED,
            Influencer.Status.REJECTED,
        }

        if status not in valid_statuses:
            logger.warning(
                "Invalid influencer status | influencer_id=%s | status=%s",
                influencer.id,
                status,
            )
            raise InvalidInfluencerStatusError(
                "Invalid status.",
            )

        current_status = influencer.status

        if current_status in {
            Influencer.Status.APPROVED,
            Influencer.Status.REJECTED,
        }:
            logger.warning(
                "Blocked status change | influencer_id=%s | current=%s",
                influencer.id,
                current_status,
            )
            raise FinalStatusModificationError(
                "Cannot modify approved/rejected influencer.",
            )

        allowed_transitions = {
            Influencer.Status.PENDING: {
                Influencer.Status.ON_HOLD,
                Influencer.Status.APPROVED,
                Influencer.Status.REJECTED,
            },
            Influencer.Status.ON_HOLD: {
                Influencer.Status.APPROVED,
                Influencer.Status.REJECTED,
            },
        }

        allowed_statuses = allowed_transitions.get(
            current_status,
            set(),
        )

        if status not in allowed_statuses:
            logger.warning(
                "Invalid influencer status transition | "
                "influencer_id=%s | current=%s | requested=%s",
                influencer.id,
                current_status,
                status,
            )
            raise InvalidStatusTransitionError(
                f"Invalid status transition from "
                f"{current_status} to {status}.",
            )

        if status == Influencer.Status.REJECTED and not reason:
            logger.warning(
                "Rejection without reason | influencer_id=%s",
                influencer.id,
            )
            raise RejectionReasonRequiredError(
                "Rejection reason is required.",
            )

        if status == Influencer.Status.APPROVED:
            InfluencerService._validate_kyc_documents(
                influencer,
            )

        influencer.status = status

        if status == Influencer.Status.REJECTED:
            influencer.rejection_reason = reason

            InfluencerService._schedule_rejection_notification(
                influencer,
                reason,
            )

        if status == Influencer.Status.APPROVED:
            completion = InfluencerService.calculate_profile_completion(
                influencer,
            )

            if completion < 100:
                logger.warning(
                    "Profile incomplete | influencer_id=%s | completion=%s",
                    influencer.id,
                    completion,
                )
                raise ProfileIncompleteError(
                    "Profile not 100% complete.",
                )

            influencer.approved_by = updated_by
            influencer.approved_at = timezone.now()

        influencer.save(
            update_fields=InfluencerService._get_status_update_fields(
                status,
            ),
        )

        if status == Influencer.Status.APPROVED:
            InfluencerService._schedule_approval_notification(
                influencer,
            )

        logger.info(
            "Influencer status updated | influencer_id=%s | "
            "from=%s | to=%s | by=%s",
            influencer.id,
            current_status,
            status,
            updated_by.id if updated_by else None,
        )

        return influencer

    @staticmethod
    def _validate_kyc_documents(
        influencer: Influencer,
    ) -> None:
        """
        Ensure all required KYC documents have been verified.
        """

        required_documents = {
            "pan",
            "aadhaar",
            "bank_proof",
        }

        verified_documents = set(
            influencer.documents.filter(is_verified=True).values_list(
                "document_type",
                flat=True,
            ),
        )

        missing_documents = required_documents - verified_documents

        if missing_documents:
            missing_document = next(
                iter(sorted(missing_documents)),
            )

            logger.warning(
                "KYC document not verified | " "influencer_id=%s | missing=%s",
                influencer.id,
                missing_document,
            )

            raise KYCVerificationError(
                f"{missing_document} document not verified.",
            )

    @staticmethod
    def _schedule_rejection_notification(
        influencer: Influencer,
        reason: str,
    ) -> None:
        """
        Schedule rejection notification after transaction commit.
        """

        notification_request = NotificationRequest(
            user=influencer.user,
            title="Application Update",
            message="Your application has been rejected.",
            category=Notification.Category.APPROVAL,
            notification_type=Notification.Type.EMAIL,
            template="rejection",
            subject="Application Status",
            context={
                "username": influencer.user.username,
                "reason": reason,
            },
            payload={
                "influencer_id": str(influencer.influencer_id),
            },
        )

        transaction.on_commit(
            lambda: NotificationService.send(
                notification_request,
            ),
        )

    @staticmethod
    def _schedule_approval_notification(
        influencer: Influencer,
    ) -> None:
        """
        Schedule approval notification after transaction commit.
        """

        notification_request = NotificationRequest(
            user=influencer.user,
            title="Account Approved",
            message=("Congratulations! Your account has been approved."),
            category=Notification.Category.APPROVAL,
            notification_type=Notification.Type.EMAIL,
            template="approval",
            subject="Account Approved",
            context={
                "username": influencer.user.username,
                "login_url": settings.FRONTEND_LOGIN_URL,
            },
            payload={
                "influencer_id": str(influencer.influencer_id),
            },
        )

        transaction.on_commit(
            lambda: NotificationService.send(
                notification_request,
            ),
        )

    @staticmethod
    def _get_status_update_fields(
        status: str,
    ) -> tuple[str, ...]:
        """
        Return the model fields that need updating for a status change.
        """

        fields = [
            "status",
        ]

        if status == Influencer.Status.REJECTED:
            fields.append("rejection_reason")

        if status == Influencer.Status.APPROVED:
            fields.extend(
                (
                    "approved_by",
                    "approved_at",
                ),
            )

        return tuple(fields)

    @staticmethod
    def calculate_profile_completion(
        influencer: Influencer,
    ) -> float:
        """
        Calculate influencer profile completion percentage.

        Completion consists of five required areas:
            - Full name
            - Phone
            - Bank account number
            - Bank name
            - Social media account
        """

        total_fields = 5
        completed_fields = 0

        profile = getattr(
            influencer,
            "profile",
            None,
        )

        if profile:
            if profile.full_name:
                completed_fields += 1

            if profile.phone:
                completed_fields += 1

        bank_detail = getattr(
            influencer,
            "bank_detail",
            None,
        )

        if bank_detail:
            if bank_detail.account_number:
                completed_fields += 1

            if bank_detail.bank_name:
                completed_fields += 1

        if influencer.social_accounts.exists():
            completed_fields += 1

        completion = (completed_fields / total_fields) * 100

        return round(
            completion,
            2,
        )
