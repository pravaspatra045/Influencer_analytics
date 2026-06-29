from django.db import models
from core.models import TimeStampedModel
from apps.users.models import User
import uuid
from django.utils import timezone


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
    influencer = models.OneToOneField(Influencer, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    
class SocialMediaAccount(TimeStampedModel):
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)

    platform = models.CharField(max_length=50)
    handle = models.CharField(max_length=100)
    followers = models.IntegerField()
    
class BankDetail(TimeStampedModel):
    influencer = models.OneToOneField(Influencer, on_delete=models.CASCADE)

    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    
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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.report_type} ({self.status})"