from pathlib import Path

from django.conf import settings
from openpyxl import Workbook


class ExcelExportError(Exception):
    """Raised when Excel export generation fails."""


def generate_influencer_excel(
    influencers,
    filename: str,
    output_directory: str | Path | None = None,
) -> str:
    """
    Generate an Excel report and return its local filesystem path.

    Args:
        influencers: Influencer queryset or iterable.
        filename: Name of the generated Excel file.
        output_directory: Directory where the temporary file should be created.
            Defaults to MEDIA_ROOT/reports for backward compatibility.
    """
    workbook = Workbook()

    worksheet = workbook.active

    if worksheet is None:
        raise ExcelExportError(
            "Unable to create Excel worksheet.",
        )

    worksheet.title = "Influencers"
    worksheet.freeze_panes = "A2"

    worksheet.append(
        [
            "Name",
            "Email",
            "Followers",
            "Status",
            "Created At",
        ],
    )

    for influencer in influencers:
        worksheet.append(
            [
                influencer.full_name,
                influencer.email,
                influencer.followers,
                influencer.status,
                influencer.created_at.strftime(
                    "%d-%m-%Y %H:%M",
                ),
            ],
        )

    reports_dir = Path(
        output_directory or Path(settings.MEDIA_ROOT) / "reports"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = reports_dir / Path(filename).name

    try:
        workbook.save(file_path)
    except Exception as exc:
        raise ExcelExportError(
            "Failed to generate Excel report.",
        ) from exc

    return str(file_path)
