import os

from rest_framework.exceptions import ValidationError


class MediaValidationService:
    """
    Handles validation of uploaded media files.
    """

    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    ALLOWED_CONTENT_TYPES = {
        "image/jpeg",
        "image/png",
        "image/webp",
    }

    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB

    @classmethod
    def validate_image(cls, image):
        """
        Validate uploaded image.
        """

        if image is None:
            raise ValidationError(
                "No image uploaded."
            )

        # ----------------------------
        # Validate extension
        # ----------------------------

        extension = os.path.splitext(
            image.name
        )[1].lower()

        if extension not in cls.IMAGE_EXTENSIONS:
            raise ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )

        # ----------------------------
        # Validate content type
        # ----------------------------

        content_type = getattr(
            image,
            "content_type",
            None,
        )

        if content_type not in cls.ALLOWED_CONTENT_TYPES:
            raise ValidationError(
                "Invalid image content type."
            )

        # ----------------------------
        # Validate size
        # ----------------------------

        if image.size > cls.MAX_IMAGE_SIZE:
            raise ValidationError(
                "Image size must not exceed 5 MB."
            )

        return image