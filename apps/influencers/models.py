from django.db import models
from core.models import TimeStampedModel
from apps.users.models import User
import uuid
from django.utils import timezone
from apps.influencers.upload_paths import (
    profile_image_upload_path,
)

class Influencer(TimeStampedModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('on_hold', 'On Hold'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    influencer_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    referral_code = models.CharField(max_length=20, blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_influencers'
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.influencer_id)
    
class InfluencerProfile(TimeStampedModel):
    """
    Stores personal information of an influencer.
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

    def __str__(self):
        return self.full_name
    
class SocialMediaAccount(TimeStampedModel):
    """
    Stores connected social media accounts.
    """

    influencer = models.ForeignKey(
        Influencer,
        on_delete=models.CASCADE,
        related_name="social_accounts",
    )

    PLATFORM_CHOICES = (
        ("INSTAGRAM", "Instagram"),
        ("YOUTUBE", "YouTube"),
        ("FACEBOOK", "Facebook"),
        ("TWITTER", "Twitter"),
        ("LINKEDIN", "LinkedIn"),
    )

    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
    )

    handle = models.CharField(
        max_length=100,
    )

    profile_url = models.URLField(
        blank=True,
    )

    followers = models.PositiveIntegerField(
        default=0,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    class Meta:
        unique_together = (
            "influencer",
            "platform",
        )

    def __str__(self):
        return f"{self.platform} - {self.handle}"
    
class BankDetail(TimeStampedModel):
    """
    Stores bank details of influencer.
    """

    influencer = models.OneToOneField(
        Influencer,
        on_delete=models.CASCADE,
        related_name="bank_detail",
    )

    account_holder_name = models.CharField(
        max_length=150,blank=True,null=True
    )

    account_number = models.CharField(
        max_length=50,
    )

    bank_name = models.CharField(
        max_length=100,blank=True,null=True
    )

    ifsc_code = models.CharField(
        max_length=20,blank=True,null=True
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

    def __str__(self):
        return self.account_holder_name
    
class Report(TimeStampedModel):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    )

    report_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    file_url = models.URLField(null=True, blank=True)

    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True
    )

    error_message = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.report_type} - {self.status}"
    
class InfluencerDocument(TimeStampedModel):
    DOCUMENT_TYPES = (
        ("pan", "PAN Card"),
        ("aadhaar", "Aadhaar"),
        ("bank_proof", "Bank Proof"),
    )

    influencer = models.ForeignKey(
        Influencer,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)

    file_url = models.URLField()

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.influencer.id} - {self.document_type}"
    

import uuid
from django.conf import settings
from django.db import models


class ExportReport(models.Model):
    """
    Stores report generation history.
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
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report_type} ({self.status})"