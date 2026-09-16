from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for the Influencer Platform.

    Extends Django's AbstractUser by adding
    role-based authorization.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        INFLUENCER = "influencer", "Influencer"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.INFLUENCER,
        db_index=True,
    )

    class Meta:
        ordering = ("username",)
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=["role"]),
        ]

    def __str__(self) -> str:
        """
        Return a human-readable representation of the user.
        """
        return f"{self.username} ({self.get_role_display()})"
