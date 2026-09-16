import logging
from pathlib import Path

from django.core.files import File

from apps.influencers.models import ExportReport

logger = logging.getLogger(__name__)


class StorageServiceError(Exception):
    """Base exception for storage-related failures."""


class StorageService:
    """Service responsible for storing generated report files."""

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
