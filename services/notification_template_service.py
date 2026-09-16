from django.template.loader import render_to_string


class NotificationTemplateService:
    """
    Handles rendering of notification templates.
    """

    @staticmethod
    def render(
        template_name,
        context,
    ):
        """
        Render HTML template.
        """

        return render_to_string(
            f"emails/{template_name}.html",
            context,
        )
