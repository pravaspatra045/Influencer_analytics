from apps.notifications.models import NotificationPreference


class NotificationPreferenceQueryService:
    """
    Handles notification preference queries.
    """

    @staticmethod
    def get_or_create(user):
        """
        Returns user's preferences.
        Creates defaults if not present.
        """

        preference, _ = NotificationPreference.objects.get_or_create(user=user)

        return preference
