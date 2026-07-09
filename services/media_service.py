from django.db import transaction

from services.media_validation_service import (
    MediaValidationService,
)
from services.storage_service import (
    StorageService,
)


class MediaService:
    """
    Handles all media-related business logic.
    """

    @staticmethod
    @transaction.atomic
    def upload_profile_image(
        influencer,
        image,
    ):
        """
        Upload or replace influencer profile image.
        """

        profile = influencer.profile

        MediaValidationService.validate_image(
            image
        )

        StorageService.replace_model_file(
            profile.profile_image,
            image,
        )

        profile.save(
            update_fields=[
                "profile_image",
            ]
        )

        return profile

    @staticmethod
    @transaction.atomic
    def delete_profile_image(
        influencer,
    ):
        """
        Delete influencer profile image.
        """

        profile = influencer.profile

        StorageService.delete_model_file(
            profile.profile_image,
        )

        profile.profile_image = None

        profile.save(
            update_fields=[
                "profile_image",
            ]
        )

        return profile