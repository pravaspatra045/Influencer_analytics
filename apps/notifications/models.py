import uuid

from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    """
    Stores notifications sent to users.
    """

    class Type(models.TextChoices):
        EMAIL = "EMAIL", "Email"
        IN_APP = "IN_APP", "In App"
        SMS = "SMS", "SMS"

    class Category(models.TextChoices):
        REGISTRATION = "REGISTRATION", "Registration"
        APPROVAL = "APPROVAL", "Approval"
        REPORT = "REPORT", "Report"
        PROFILE = "PROFILE", "Profile"
        SYSTEM = "SYSTEM", "System"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    notification_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    payload = models.JSONField(
        default=dict,
        blank=True,
    )

    notification_type = models.CharField(
        max_length=20,
        choices=Type.choices,
        default=Type.IN_APP,
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.SYSTEM,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    is_read = models.BooleanField(
        default=False,
    )

    read_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    is_deleted = models.BooleanField(
        default=False,
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return (
            f"{self.title} "
            f"({self.notification_type}) "
            f"- {self.user.email}"
        )


class NotificationPreference(TimeStampedModel):
    """
    Stores user notification preferences.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
    )

    registration_email = models.BooleanField(
        default=True,
    )

    registration_in_app = models.BooleanField(
        default=True,
    )

    approval_email = models.BooleanField(
        default=True,
    )

    approval_in_app = models.BooleanField(
        default=True,
    )

    report_email = models.BooleanField(
        default=True,
    )

    report_in_app = models.BooleanField(
        default=True,
    )

    profile_email = models.BooleanField(
        default=False,
    )

    profile_in_app = models.BooleanField(
        default=True,
    )

    system_email = models.BooleanField(
        default=True,
    )

    system_in_app = models.BooleanField(
        default=True,
    )

    def __str__(self):
        return f"Preferences - {self.user.email}"


class BulkNotification(TimeStampedModel):
    """
    Tracks bulk notification jobs.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    class RecipientType(models.TextChoices):
        ALL_USERS = "ALL_USERS", "All Users"
        ALL_INFLUENCERS = "ALL_INFLUENCERS", "All Influencers"
        SELECTED_USERS = "SELECTED_USERS", "Selected Users"

    bulk_notification_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bulk_notifications",
    )

    title = models.CharField(
        max_length=255,
    )

    message = models.TextField()

    category = models.CharField(
        max_length=30,
        choices=Notification.Category.choices,
    )

    notification_type = models.CharField(
        max_length=20,
        choices=Notification.Type.choices,
    )

    template = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    subject = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    recipient_type = models.CharField(
        max_length=30,
        choices=RecipientType.choices,
        default=RecipientType.ALL_USERS,
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
    )

    total_users = models.PositiveIntegerField(
        default=0,
    )

    processed_users = models.PositiveIntegerField(
        default=0,
    )

    failed_users = models.PositiveIntegerField(
        default=0,
    )

    task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    started_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    completed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return f"{self.title} " f"({self.status})"

    @property
    def progress(self):
        """
        Returns completion percentage.
        """

        if self.total_users == 0:
            return 0

        return round(
            (self.processed_users / self.total_users) * 100,
            2,
        )
