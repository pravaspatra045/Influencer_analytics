import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """
    Factory for User model.
    """

    class Meta:
        model = User
        django_get_or_create = ("username",)

        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")

    first_name = factory.Faker("first_name")

    last_name = factory.Faker("last_name")

    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")

    role = "influencer"

    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """
        Sets password after object creation.
        """

        password = extracted or "Password@123"

        self.set_password(password)

        if create:
            self.save(update_fields=["password"])
