import logging
from pathlib import Path
from uuid import uuid4

from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile

logger = logging.getLogger(__name__)


class MediaServiceError(Exception):
    """Base exception for media-related failures."""


class MediaService:
    """Centralized handling of uploaded media files."""

    @staticmethod
    def save(
        uploaded_file: UploadedFile,
        directory: str,
    ) -> str:
        """
        Save an uploaded file using Django's configured storage.
        """

        if not uploaded_file:
            raise MediaServiceError(
                "No file was provided.",
            )

        directory = directory.strip("/")

        if not directory:
            raise MediaServiceError(
                "Media directory is required.",
            )

        original_name = Path(uploaded_file.name or "").name
        extension = Path(original_name).suffix.lower()

        filename = f"{uuid4().hex}{extension}"
        file_path = f"{directory}/{filename}"

        try:
            saved_path = default_storage.save(
                file_path,
                uploaded_file,
            )

        except Exception as exc:
            logger.exception(
                "Failed to save media file | directory=%s",
                directory,
            )
            raise MediaServiceError(
                "Failed to save media file.",
            ) from exc

        logger.info(
            "Media file saved | path=%s",
            saved_path,
        )

        return saved_path

    @staticmethod
    def delete(
        file_path: str | None,
    ) -> None:
        """
        Delete a media file using Django's configured storage.
        """

        if not file_path:
            return

        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)

                logger.info(
                    "Media file deleted | path=%s",
                    file_path,
                )

        except Exception as exc:
            logger.exception(
                "Failed to delete media file | path=%s",
                file_path,
            )
            raise MediaServiceError(
                "Failed to delete media file.",
            ) from exc
