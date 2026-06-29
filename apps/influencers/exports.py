import os

from django.conf import settings
from openpyxl import Workbook


def generate_influencer_excel(influencers, filename):
    """
    Generate influencer excel report.
    """

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Influencers"

    worksheet.freeze_panes = "A2"

    worksheet.append([
        "Name",
        "Email",
        "Followers",
        "Status",
        "Created At",
    ])

    for influencer in influencers:
        worksheet.append([
            influencer.full_name,
            influencer.email,
            influencer.followers,
            influencer.status,
            influencer.created_at.strftime("%d-%m-%Y %H:%M"),
        ])

    reports_dir = os.path.join(settings.MEDIA_ROOT, "reports")

    os.makedirs(reports_dir, exist_ok=True)

    file_path = os.path.join(reports_dir, filename)

    workbook.save(file_path)

    return file_path