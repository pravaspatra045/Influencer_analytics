import boto3
from django.conf import settings

import uuid


class StorageService:

    @staticmethod
    def upload_file(file_obj, folder="documents"):
        """
        Upload file to S3 and return URL
        """

        filename = f"{folder}/{uuid.uuid4()}_{file_obj.name}"

        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        s3.upload_fileobj(
            file_obj,
            settings.AWS_BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": file_obj.content_type}
        )

        return f"https://{settings.AWS_BUCKET_NAME}.s3.amazonaws.com/{filename}"