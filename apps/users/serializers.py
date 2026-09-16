from typing import Any

from django.contrib.auth import authenticate
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    """
    Serializer for authenticating users.
    """

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validate user credentials.
        """

        username = attrs["username"]
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if not user or not user.is_active:
            raise serializers.ValidationError(
                {
                    "non_field_errors": [
                        "Invalid username or password.",
                    ]
                }
            )

        attrs["user"] = user

        return attrs
