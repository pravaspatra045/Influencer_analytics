import os

from django.core.files.base import File
from django.core.files.storage import default_storage

from datetime import timedelta
from django.conf import settings
import boto3


class StorageService:
    """
    Centralized service for all storage operations.
    """

    @staticmethod
    def save(file_name, file_obj):
        return default_storage.save(
            file_name,
            file_obj,
        )

    @staticmethod
    def open(file_name, mode="rb"):
        return default_storage.open(
            file_name,
            mode,
        )

    @staticmethod
    def delete(file_name):
        if default_storage.exists(file_name):
            default_storage.delete(file_name)

    @staticmethod
    def exists(file_name):
        return default_storage.exists(file_name)

    @staticmethod
    def url(file_name):
        return default_storage.url(file_name)

    @staticmethod
    def size(file_name):
        return default_storage.size(file_name)

    @staticmethod
    def save_model_file(file_field, local_file_path):
        """
        Save a local file into a Django FileField.
        """

        file_name = os.path.basename(local_file_path)

        with open(local_file_path, "rb") as f:
            file_field.save(
                file_name,
                File(f),
                save=False,
            )

    @staticmethod
    def save_report_file(report, local_file_path):
        """
        Save generated report to configured storage.
        """

        StorageService.save_model_file(
            report.file,
            local_file_path,
        )

        report.save(
            update_fields=["file"]
        )

    @staticmethod
    def delete_local_file(local_file_path):
        """
        Delete temporary local file.
        """

        if os.path.exists(local_file_path):
            os.remove(local_file_path)
            
    @staticmethod
    def generate_presigned_url(file_name, expiration=600):
        """
        Generate a temporary download URL from S3.

        expiration: seconds (default 10 minutes)
        """

        client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )

        return client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
                "Key": file_name,
            },
            ExpiresIn=expiration,
        )
        
    @staticmethod
    def delete_model_file(file_field):
        """
        Delete an existing file from storage.
        """

        if file_field and file_field.name:
            default_storage.delete(file_field.name)


    @staticmethod
    def replace_model_file(
        file_field,
        uploaded_file,
    ):
        """
        Replace existing file.

        upload_to callable defined on the model
        will automatically generate the correct path.
        """

        StorageService.delete_model_file(
            file_field
        )

        file_field.save(
            uploaded_file.name,
            uploaded_file,
            save=False,
        )

        return file_field