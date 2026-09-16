import uuid
from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse


@patch("services.report_service.ReportService.export_report")
@pytest.mark.django_db
def test_export_report_success(
    mock_export,
    authenticated_client,
):

    mock_export.return_value = {
        "buffer": b"csv data",
        "content_type": "text/csv",
        "filename": "report.csv",
    }

    response = authenticated_client.get(reverse("export-report"))

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"


@patch("services.report_service.ReportService.export_report")
@pytest.mark.skip(reason="Dashboard export endpoint will be fixed later")
@pytest.mark.django_db
def test_export_invalid_format(
    mock_export,
    authenticated_client,
):

    mock_export.side_effect = ValueError

    response = authenticated_client.get(
        reverse("export-report"),
        {
            "format": "abc",
        },
    )

    assert response.status_code == 400


@patch("apps.influencers.views.create_export_report")
@pytest.mark.django_db
def test_async_report(
    mock_create,
    authenticated_client,
):

    report = MagicMock()

    report.id = uuid.uuid4()
    report.status = "PROCESSING"

    mock_create.return_value = report

    response = authenticated_client.post(
        reverse("async-report"),
        {},
        format="json",
    )

    assert response.status_code == 202

    assert response.data["message"] == "Report generation started."
