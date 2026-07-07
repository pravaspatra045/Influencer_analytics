from apps.influencers.tasks import generate_influencer_report


class ReportDispatcher:
    """
    Responsible for dispatching report-related background tasks.
    """

    @staticmethod
    def dispatch(report):
        """
        Queue a report generation task.
        """

        task = generate_influencer_report.delay(
            str(report.id)
        )

        report.task_id = task.id

        report.save(update_fields=["task_id"])

        return task

    @staticmethod
    def retry(report):
        """
        Retry an existing report.
        """

        return ReportDispatcher.dispatch(report)