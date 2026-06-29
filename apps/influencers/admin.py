from django.contrib import admin
from .models import (
    Influencer,
    InfluencerProfile,
    SocialMediaAccount,
    BankDetail,
)

admin.site.register(Influencer)
admin.site.register(InfluencerProfile)
admin.site.register(SocialMediaAccount)
admin.site.register(BankDetail)
from .models import ExportReport

@admin.register(ExportReport)
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
    )

    search_fields = (
        "task_id",
        "user__email",
    )