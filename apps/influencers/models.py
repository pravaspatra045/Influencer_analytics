import uuid

from django.conf import settings
from django.db import models

from apps.influencers.upload_paths import profile_image_upload_path
from core.models import TimeStampedModel


class Influencer(TimeStampedModel):
    """
    Represents the influencer application and approval state.

    Each influencer is associated with exactly one user account.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ON_HOLD = "on_hold", "On Hold"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="influencer",
    )

    influencer_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    referral_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_influencers",
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Influencer"
        verbose_name_plural = "Influencers"
        indexes = (
            models.Index(
                fields=("status", "created_at"),
                name="influencer_status_created_idx",
            ),
        )

    def __str__(self) -> str:
        """Return the public influencer identifier."""
        return str(self.influencer_id)


class InfluencerProfile(TimeStampedModel):
    """
    Stores personal and profile information for an influencer.
    """

    influencer = models.OneToOneField(
        Influencer,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    full_name = models.CharField(
        max_length=100,
    )

    phone = models.CharField(
        max_length=15,
    )

    profile_image = models.ImageField(
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
    )

    bio = models.TextField(
        blank=True,
        default="",
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    state = models.CharField(
        max_length=100,
        blank=True,
    )

    country = models.CharField(
        max_length=100,
        blank=True,
    )

    pincode = models.CharField(
        max_length=10,
        blank=True,
    )

    class Meta:
        verbose_name = "Influencer Profile"
        verbose_name_plural = "Influencer Profiles"

    def __str__(self) -> str:
        """Return the influencer's full name."""
        return self.full_name


class SocialMediaAccount(TimeStampedModel):
    """
    Stores a social media account connected to an influencer.
    """

    class Platform(models.TextChoices):
        INSTAGRAM = "INSTAGRAM", "Instagram"
        YOUTUBE = "YOUTUBE", "YouTube"
        FACEBOOK = "FACEBOOK", "Facebook"
        TWITTER = "TWITTER", "Twitter"
        LINKEDIN = "LINKEDIN", "LinkedIn"

    influencer = models.ForeignKey(
        Influencer,
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )

    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
    )

    handle = models.CharField(
        max_length=100,
    )

    profile_url = models.URLField(
        blank=True,
    )

    followers = models.PositiveIntegerField(
        default=0,
        db_index=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name = "Social Media Account"
        verbose_name_plural = "Social Media Accounts"
        constraints = (
            models.UniqueConstraint(
                fields=("influencer", "platform"),
                name="unique_influencer_platform",
            ),
        )

    def __str__(self) -> str:
        """Return the platform and account handle."""
        return f"{self.get_platform_display()} - {self.handle}"


class BankDetail(TimeStampedModel):
    """
    Stores bank and payment details associated with an influencer.
    """

    influencer = models.OneToOneField(
        Influencer,
        on_delete=models.CASCADE,
        related_name="bank_detail",
    )

    account_holder_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
    )

    account_number = models.CharField(
        max_length=50,
    )

    bank_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    ifsc_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    upi_id = models.CharField(
        max_length=100,
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    class Meta:
        verbose_name = "Bank Detail"
        verbose_name_plural = "Bank Details"

    def __str__(self) -> str:
        """Return a safe human-readable bank detail representation."""
        return self.account_holder_name or self.account_number


class Report(TimeStampedModel):
    """
    Represents a legacy/synchronous report record.
    """

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    report_type = models.CharField(
        max_length=50,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )

    file_url = models.URLField(
        null=True,
        blank=True,
    )

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_reports",
    )

    error_message = models.TextField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Report"
        verbose_name_plural = "Reports"

    def __str__(self) -> str:
        """Return the report type and current status."""
        return f"{self.report_type} - {self.get_status_display()}"


class InfluencerDocument(TimeStampedModel):
    """
    Stores KYC and verification documents submitted by an influencer.
    """

    class DocumentType(models.TextChoices):
        PAN = "pan", "PAN Card"
        AADHAAR = "aadhaar", "Aadhaar"
        BANK_PROOF = "bank_proof", "Bank Proof"

    influencer = models.ForeignKey(
        Influencer,
        on_delete=models.CASCADE,
        related_name="documents",
    )

    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
    )

    file_url = models.URLField()

    is_verified = models.BooleanField(
        default=False,
        db_index=True,
    )

    class Meta:
        verbose_name = "Influencer Document"
        verbose_name_plural = "Influencer Documents"
        indexes = (
            models.Index(
                fields=("influencer", "document_type"),
                name="document_influencer_type_idx",
            ),
        )

    def __str__(self) -> str:
        """Return the influencer and document type."""
        return (
            f"{self.influencer.influencer_id} - "
            f"{self.get_document_type_display()}"
        )


class ExportReport(models.Model):
    """
    Stores asynchronous report/export generation history.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="export_reports",
    )

    task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    report_type = models.CharField(
        max_length=100,
        default="INFLUENCER_EXPORT",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    file = models.FileField(
        upload_to="reports/",
        blank=True,
        null=True,
    )

    error_message = models.TextField(
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    filters = models.JSONField(
        default=dict,
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Export Report"
        verbose_name_plural = "Export Reports"
        indexes = (
            models.Index(
                fields=("user", "-created_at"),
                name="export_user_created_idx",
            ),
            models.Index(
                fields=("status", "-created_at"),
                name="export_status_created_idx",
            ),
        )

    def __str__(self) -> str:
        """Return the report type and current status."""
        return f"{self.report_type} ({self.get_status_display()})"
