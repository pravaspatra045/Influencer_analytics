from django.utils.timesince import timesince
from rest_framework import serializers

from apps.notifications.models import (
    BulkNotification,
    Notification,
    NotificationPreference,
)


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notification details.
    """

    time_ago = serializers.SerializerMethodField()

    class Meta:
        model = Notification

        fields = (
            "notification_id",
            "title",
            "message",
            "category",
            "notification_type",
            "status",
            "is_read",
            "read_at",
            "payload",
            "created_at",
            "time_ago",
        )

    def get_time_ago(self, obj):
        """
        Returns a human readable relative time.
        Example:
            2 minutes ago
            5 hours ago
            3 days ago
        """

        if not obj.created_at:
            return None

        return f"{timesince(obj.created_at)} ago"


class NotificationPreferenceSerializer(serializers.ModelSerializer):

    class Meta:

        model = NotificationPreference

        exclude = ("id",)


class BulkNotificationCreateSerializer(serializers.Serializer):
    """
    Serializer for creating bulk notification jobs.
    """

    title = serializers.CharField(
        max_length=255,
    )

    message = serializers.CharField()

    category = serializers.ChoiceField(
        choices=Notification.Category.choices,
    )

    notification_type = serializers.ChoiceField(
        choices=Notification.Type.choices,
    )

    recipient_type = serializers.ChoiceField(
        choices=BulkNotification.RecipientType.choices,
    )

    template = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    subject = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    payload = serializers.JSONField(
        required=False,
    )


class BulkNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for bulk notification jobs.
    """

    progress = serializers.ReadOnlyField()

    class Meta:
        model = BulkNotification

        fields = (
            "bulk_notification_id",
            "title",
            "message",
            "category",
            "notification_type",
            "recipient_type",
            "status",
            "total_users",
            "processed_users",
            "failed_users",
            "progress",
            "started_at",
            "completed_at",
            "created_at",
        )
