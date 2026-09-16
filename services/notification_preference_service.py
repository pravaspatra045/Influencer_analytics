from apps.notifications.models import Notification
from services.notification_preference_query_service import (
    NotificationPreferenceQueryService,
)


class NotificationPreferenceService:
    """
    Handles notification preference logic.
    """

    CATEGORY_MAPPING = {
        Notification.Category.REGISTRATION: {
            Notification.Type.EMAIL: "registration_email",
            Notification.Type.IN_APP: "registration_in_app",
        },
        Notification.Category.APPROVAL: {
            Notification.Type.EMAIL: "approval_email",
            Notification.Type.IN_APP: "approval_in_app",
        },
        Notification.Category.REPORT: {
            Notification.Type.EMAIL: "report_email",
            Notification.Type.IN_APP: "report_in_app",
        },
        Notification.Category.PROFILE: {
            Notification.Type.EMAIL: "profile_email",
            Notification.Type.IN_APP: "profile_in_app",
        },
        Notification.Category.SYSTEM: {
            Notification.Type.EMAIL: "system_email",
            Notification.Type.IN_APP: "system_in_app",
        },
    }

    @classmethod
    def can_send(
        cls,
        user,
        category,
        notification_type,
    ):

        preference = NotificationPreferenceQueryService.get_or_create(user)

        field = cls.CATEGORY_MAPPING.get(category, {}).get(notification_type)

        if not field:
            return True

        return getattr(
            preference,
            field,
        )
