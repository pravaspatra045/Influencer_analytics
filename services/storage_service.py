import os

from django.core.files import File


class StorageService:
    """
    Handles storing generated files.

    Today:
        Local Media Storage

    Future:
        AWS S3
        Azure Blob
        GCP Storage
    """

    @staticmethod
    def save_report_file(report, file_path, filename):
        """
        Save generated report file.
        """

        with open(file_path, "rb") as report_file:

            report.file.save(
                filename,
                File(report_file),
                save=False,
            )

        report.save(update_fields=["file"])

    @staticmethod
    def delete_local_file(file_path):
        """
        Delete temporary local file.
        """

        if os.path.exists(file_path):
            os.remove(file_path)