import factory
from factory.django import DjangoModelFactory

from apps.notifications.models import NotificationPreference
from tests.factories.user_factory import UserFactory


class NotificationPreferenceFactory(DjangoModelFactory):

    class Meta:
        model = NotificationPreference

    user = factory.SubFactory(UserFactory)

    registration_email = True
    registration_in_app = True

    approval_email = True
    approval_in_app = True

    report_email = True
    report_in_app = True

    profile_email = False
    profile_in_app = True

    system_email = True
    system_in_app = True
