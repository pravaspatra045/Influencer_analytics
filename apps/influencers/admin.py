from django.contrib import admin

from .models import (
    BankDetail,
    ExportReport,
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
)

admin.site.register(Influencer)
admin.site.register(InfluencerProfile)
admin.site.register(SocialMediaAccount)
admin.site.register(BankDetail)
admin.site.register(ExportReport)


class ExportReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "report_type",
        "status",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "status",
        "report_type",
        # "is_read",
        # "is_deleted",
    )

    search_fields = (
        "task_id",
        "user__email",
    )
