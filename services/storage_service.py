import logging
from pathlib import Path
from uuid import uuid4

from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile

from apps.influencers.models import ExportReport

logger = logging.getLogger(__name__)


class StorageServiceError(Exception):
    """Base exception for storage-related failures."""


class StorageService:
    """Service responsible for storing application files."""

    # Maximum size for KYC documents: 10 MB
    MAX_DOCUMENT_SIZE = 10 * 1024 * 1024

    # Only these file formats are accepted for KYC documents.
    ALLOWED_DOCUMENT_TYPES = {
        ".pdf": {
            "application/pdf",
        },
        ".jpg": {
            "image/jpeg",
        },
        ".jpeg": {
            "image/jpeg",
        },
        ".png": {
            "image/png",
        },
    }

    @staticmethod
    def upload_file(
        uploaded_file: UploadedFile,
    ) -> str:
        """
        Validate and upload an influencer KYC document.

        Returns:
            Public storage URL for the uploaded document.
        """

        if not uploaded_file:
            raise StorageServiceError(
                "No file was provided.",
            )

        # ------------------------------------------------------------------
        # File size validation
        # ------------------------------------------------------------------

        if uploaded_file.size > StorageService.MAX_DOCUMENT_SIZE:
            raise StorageServiceError(
                "File size must not exceed 10 MB.",
            )

        # ------------------------------------------------------------------
        # Filename validation
        # ------------------------------------------------------------------

        original_name = Path(
            uploaded_file.name or "",
        ).name

        if not original_name:
            raise StorageServiceError(
                "Invalid file name.",
            )

        extension = Path(
            original_name,
        ).suffix.lower()

        if extension not in StorageService.ALLOWED_DOCUMENT_TYPES:
            raise StorageServiceError(
                "Unsupported file type. "
                "Only PDF, JPG, JPEG, and PNG files are allowed.",
            )

        # ------------------------------------------------------------------
        # Content-type validation
        # ------------------------------------------------------------------

        content_type = (uploaded_file.content_type or "").lower()

        allowed_content_types = StorageService.ALLOWED_DOCUMENT_TYPES[
            extension
        ]

        if content_type not in allowed_content_types:
            raise StorageServiceError(
                "File content type does not match the file extension.",
            )

        # ------------------------------------------------------------------
        # Generate server-controlled storage path
        # ------------------------------------------------------------------

        filename = f"{uuid4().hex}{extension}"

        storage_path = f"influencer_documents/{filename}"

        # ------------------------------------------------------------------
        # Store file
        # ------------------------------------------------------------------

        try:
            saved_path = default_storage.save(
                storage_path,
                uploaded_file,
            )

            file_url = default_storage.url(
                saved_path,
            )

        except Exception as exc:
            logger.exception(
                "Failed to upload influencer document.",
            )

            raise StorageServiceError(
                "Failed to upload document.",
            ) from exc

        logger.info(
            "Influencer document uploaded | path=%s",
            saved_path,
        )

        return file_url

    @staticmethod
    def save_report_file(
        report: ExportReport,
        file_path: str | Path,
    ) -> str:
        """
        Save a generated report through Django's FileField.
        """

        source_path = Path(file_path)

        if not source_path.is_file():
            raise StorageServiceError(
                f"Report file does not exist: {source_path}",
            )

        try:
            with source_path.open("rb") as report_file:
                report.file.save(
                    source_path.name,
                    File(report_file),
                    save=False,
                )

            report.save(
                update_fields=("file",),
            )

        except Exception as exc:
            logger.exception(
                "Failed to store report file | report_id=%s",
                report.id,
            )

            raise StorageServiceError(
                "Failed to store report file.",
            ) from exc

        logger.info(
            "Report file stored | report_id=%s | filename=%s",
            report.id,
            source_path.name,
        )

        return report.file.name

    @staticmethod
    def delete_local_file(
        file_path: str | Path,
    ) -> None:
        """Delete a temporary local report file if it exists."""

        path = Path(file_path)

        if not path.is_file():
            return

        try:
            path.unlink()

            logger.info(
                "Temporary report file deleted | path=%s",
                path,
            )

        except Exception as exc:
            logger.exception(
                "Failed to delete temporary report file | path=%s",
                path,
            )

            raise StorageServiceError(
                "Failed to delete temporary report file.",
            ) from exc
