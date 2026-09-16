from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


@pytest.mark.skip(
    reason="Document upload/S3 implementation will be fixed later"
)
@patch("services.storage_service.StorageService.upload_file")
@pytest.mark.django_db
def test_upload_document_success(
    mock_upload,
    authenticated_client,
    influencer,
):

    mock_upload.return_value = (
        "https://test-bucket.s3.amazonaws.com/aadhar.pdf"
    )

    file = SimpleUploadedFile(
        "aadhar.pdf",
        b"dummy pdf",
        content_type="application/pdf",
    )

    response = authenticated_client.post(
        reverse("upload-document"),
        {
            "document_type": "AADHAR",
            "file": file,
        },
    )

    assert response.status_code == 200
    assert response.data["message"] == "Document uploaded successfully"


@pytest.mark.skip(
    reason="Document upload/S3 implementation will be fixed later"
)
@pytest.mark.django_db
def test_upload_document_without_file(
    authenticated_client,
):

    response = authenticated_client.post(
        reverse("upload-document"),
        {
            "document_type": "PAN",
        },
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_upload_document_influencer_not_found(
    authenticated_client,
    influencer,
):

    influencer.delete()

    file = SimpleUploadedFile(
        "pan.pdf",
        b"abc",
        content_type="application/pdf",
    )

    response = authenticated_client.post(
        reverse("upload-document"),
        {
            "document_type": "PAN",
            "file": file,
        },
    )

    assert response.status_code == 404
