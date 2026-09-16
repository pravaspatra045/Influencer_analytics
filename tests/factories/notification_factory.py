import factory
from factory.django import DjangoModelFactory

from apps.notifications.models import Notification
from tests.factories.user_factory import UserFactory


class NotificationFactory(DjangoModelFactory):
    class Meta:
        model = Notification

    user = factory.SubFactory(UserFactory)

    title = factory.Sequence(lambda n: f"Notification {n}")

    message = factory.Faker("sentence")

    category = Notification.Category.SYSTEM

    notification_type = Notification.Type.IN_APP

    status = Notification.Status.PENDING

    is_read = False

    payload = {}
