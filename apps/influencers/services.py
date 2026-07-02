from apps.influencers.models import ExportReport
from apps.influencers.tasks import generate_influencer_report


def create_export_report(
    user,
    filters=None,
    report_type="INFLUENCER_EXPORT",
):

    report = ExportReport.objects.create(
        user=user,
        report_type=report_type,
        filters=filters or {},
        status=ExportReport.Status.PENDING,
    )

    task = generate_influencer_report.delay(str(report.id))

    report.task_id = task.id
    report.save(update_fields=["task_id"])

    return report