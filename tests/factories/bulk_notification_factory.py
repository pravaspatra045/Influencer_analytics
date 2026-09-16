import factory
from factory.django import DjangoModelFactory

from apps.notifications.models import BulkNotification, Notification
from tests.factories.user_factory import UserFactory


class BulkNotificationFactory(DjangoModelFactory):

    class Meta:
        model = BulkNotification

    created_by = factory.SubFactory(UserFactory)

    title = factory.Sequence(lambda n: f"Bulk Notification {n}")

    message = factory.Faker("sentence")

    category = Notification.Category.SYSTEM

    notification_type = Notification.Type.IN_APP

    recipient_type = BulkNotification.RecipientType.ALL_USERS

    payload = {}

    status = BulkNotification.Status.PENDING
