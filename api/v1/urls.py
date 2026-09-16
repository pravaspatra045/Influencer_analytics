from django.urls import path

from apps.influencers.views import (
    ApprovalTimeAnalyticsAPI,
    AsyncReportAPI,
    DashboardStatsAPI,
    DeleteProfileImageAPI,
    DownloadReportAPI,
    ExportInfluencersAPI,
    GrowthRateAPI,
    InfluencerApprovalAPI,
    InfluencerDocumentsAPI,
    InfluencerListAPI,
    InfluencerRegistrationAPI,
    InfluencerReviewAPI,
    InfluencerTrendAPI,
    MyProfileAPI,
    MyReportsAPI,
    RecentInfluencersAPI,
    RejectionInsightsAPI,
    RejectionRateAPI,
    ReportStatisticsAPI,
    ReportStatusAPI,
    RetryReportAPI,
    SecureReportDownloadAPI,
    StatusDistributionAPI,
    UpdateMyProfileAPI,
    UploadDocumentAPI,
    UploadProfileImageAPI,
    VerifyDocumentAPI,
)
from apps.notifications.views import (
    BulkNotificationCreateAPIView,
    BulkNotificationDetailAPIView,
    BulkNotificationListAPIView,
    DeleteNotificationAPI,
    MarkAllNotificationsReadAPI,
    MarkNotificationReadAPI,
    NotificationDetailAPI,
    NotificationListAPI,
    NotificationPreferenceAPI,
    UnreadNotificationCountAPI,
)
from apps.users.views import LoginAPI

urlpatterns = [
    # ============================================================
    # Authentication
    # ============================================================
    path(
        "login/",
        LoginAPI.as_view(),
        name="login",
    ),
    # ============================================================
    # Influencer
    # ============================================================
    path(
        "register/",
        InfluencerRegistrationAPI.as_view(),
        name="register",
    ),
    path(
        "influencer/<int:pk>/status/",
        InfluencerApprovalAPI.as_view(),
        name="approve-influencer",
    ),
    path(
        "influencers-list/",
        InfluencerListAPI.as_view(),
        name="influencer-list",
    ),
    path(
        "my-profile/",
        MyProfileAPI.as_view(),
        name="my-profile",
    ),
    path(
        "profile/update/",
        UpdateMyProfileAPI.as_view(),
        name="update-profile",
    ),
    path(
        "profile/upload-image/",
        UploadProfileImageAPI.as_view(),
        name="upload-profile-image",
    ),
    path(
        "profile/delete-image/",
        DeleteProfileImageAPI.as_view(),
        name="delete-profile-image",
    ),
    # ============================================================
    # Dashboard
    # ============================================================
    path(
        "dashboard/stats/",
        DashboardStatsAPI.as_view(),
        name="dashboard-stats",
    ),
    path(
        "dashboard/recent/",
        RecentInfluencersAPI.as_view(),
        name="recent-influencers",
    ),
    path(
        "dashboard/trends/",
        InfluencerTrendAPI.as_view(),
        name="dashboard-trend",
    ),
    path(
        "dashboard/status-distribution/",
        StatusDistributionAPI.as_view(),
        name="status-distribution",
    ),
    path(
        "dashboard/growth/",
        GrowthRateAPI.as_view(),
        name="growth-rate",
    ),
    path(
        "dashboard/approval-time/",
        ApprovalTimeAnalyticsAPI.as_view(),
        name="approval-time",
    ),
    path(
        "dashboard/rejection-insights/",
        RejectionInsightsAPI.as_view(),
        name="rejection-insights",
    ),
    path(
        "dashboard/rejection-rate/",
        RejectionRateAPI.as_view(),
        name="rejection-rate",
    ),
    path(
        "dashboard/export/",
        ExportInfluencersAPI.as_view(),
        name="export-report",
    ),
    path(
        "dashboard/async-report/",
        AsyncReportAPI.as_view(),
        name="async-report",
    ),
    path(
        "dashboard/report-status/<int:report_id>/",
        ReportStatusAPI.as_view(),
        name="report-status",
    ),
    # ============================================================
    # Influencer Documents
    # ============================================================
    path(
        "upload-document/",
        UploadDocumentAPI.as_view(),
        name="upload-document",
    ),
    path(
        "documents/<int:influencer_id>/",
        InfluencerDocumentsAPI.as_view(),
        name="influencer-documents",
    ),
    path(
        "verify-document/<int:doc_id>/",
        VerifyDocumentAPI.as_view(),
        name="verify-document",
    ),
    # ============================================================
    # Influencer Review
    # ============================================================
    path(
        "influencer-review/<int:influencer_id>/",
        InfluencerReviewAPI.as_view(),
        name="influencer-review",
    ),
    # ============================================================
    # My Reports
    # ============================================================
    path(
        "reports/",
        MyReportsAPI.as_view(),
        name="my-reports",
    ),
    path(
        "reports/<uuid:report_id>/download/",
        DownloadReportAPI.as_view(),
        name="download-report",
    ),
    path(
        "reports/<uuid:report_id>/retry/",
        RetryReportAPI.as_view(),
        name="retry-report",
    ),
    path(
        "reports/statistics/",
        ReportStatisticsAPI.as_view(),
        name="report-statistics",
    ),
    path(
        "reports/<uuid:report_id>/secure-download/",
        SecureReportDownloadAPI.as_view(),
        name="secure-report-download",
    ),
    # ============================================================
    # Notifications
    # ============================================================
    path(
        "",
        NotificationListAPI.as_view(),
        name="notification-list",
    ),
    path(
        "<uuid:notification_id>/",
        NotificationDetailAPI.as_view(),
        name="notification-detail",
    ),
    path(
        "<uuid:notification_id>/read/",
        MarkNotificationReadAPI.as_view(),
        name="notification-read",
    ),
    path(
        "read-all/",
        MarkAllNotificationsReadAPI.as_view(),
        name="notification-read-all",
    ),
    path(
        "<uuid:notification_id>/delete/",
        DeleteNotificationAPI.as_view(),
        name="notification-delete",
    ),
    path(
        "unread-count/",
        UnreadNotificationCountAPI.as_view(),
        name="notification-unread-count",
    ),
    path(
        "preferences/",
        NotificationPreferenceAPI.as_view(),
        name="notification-preferences",
    ),
    # ============================================================
    # Bulk Notifications
    # ============================================================
    path(
        "bulk-notifications/",
        BulkNotificationListAPIView.as_view(),
        name="bulk-notification-list",
    ),
    path(
        "bulk-notifications/create/",
        BulkNotificationCreateAPIView.as_view(),
        name="bulk-notification-create",
    ),
    path(
        "bulk-notifications/<uuid:bulk_notification_id>/",
        BulkNotificationDetailAPIView.as_view(),
        name="bulk-notification-detail",
    ),
]


"""from django.urls import path

from apps.influencers.views import (
    ApprovalTimeAnalyticsAPI,
    AsyncReportAPI,
    DashboardStatsAPI,
    DeleteProfileImageAPI,
    DownloadReportAPI,
    ExportInfluencersAPI,
    GrowthRateAPI,
    InfluencerApprovalAPI,
    InfluencerDocumentsAPI,
    InfluencerListAPI,
    InfluencerRegistrationAPI,
    InfluencerReviewAPI,
    InfluencerTrendAPI,
    MyProfileAPI,
    MyReportsAPI,
    RecentInfluencersAPI,
    RejectionInsightsAPI,
    RejectionRateAPI,
    ReportStatisticsAPI,
    ReportStatusAPI,
    RetryReportAPI,
    SecureReportDownloadAPI,
    StatusDistributionAPI,
    UpdateMyProfileAPI,
    UploadDocumentAPI,
    UploadProfileImageAPI,
    VerifyDocumentAPI,
)
from apps.notifications.views import (
    BulkNotificationCreateAPIView,
    BulkNotificationDetailAPIView,
    BulkNotificationListAPIView,
    DeleteNotificationAPI,
    MarkAllNotificationsReadAPI,
    MarkNotificationReadAPI,
    NotificationDetailAPI,
    NotificationListAPI,
    NotificationPreferenceAPI,
    UnreadNotificationCountAPI,
)
from apps.users.views import LoginAPI

urlpatterns = [
    # Auth
    path("login/", LoginAPI.as_view(), name="login"),
    # influencer
    path("register/", InfluencerRegistrationAPI.as_view()),
    path("influencer/<int:pk>/status/", InfluencerApprovalAPI.as_view()),
    path("influencers-list/", InfluencerListAPI.as_view()),
    path("my-profile/", MyProfileAPI.as_view()),
    path(
        "profile/update/",
        UpdateMyProfileAPI.as_view(),
        name="update-profile",
    ),
    path(
        "profile/upload-image/",
        UploadProfileImageAPI.as_view(),
        name="upload-profile-image",
    ),
    path(
        "profile/delete-image/",
        DeleteProfileImageAPI.as_view(),
        name="delete-profile-image",
    ),
    # dashboard apis
    path("dashboard/stats/", DashboardStatsAPI.as_view()),
    path("dashboard/recent/", RecentInfluencersAPI.as_view()),
    path("dashboard/trends/", InfluencerTrendAPI.as_view()),
    path("dashboard/status-distribution/", StatusDistributionAPI.as_view()),
    path("dashboard/growth/", GrowthRateAPI.as_view()),
    path("dashboard/approval-time/", ApprovalTimeAnalyticsAPI.as_view()),
    path("dashboard/rejection-insights/", RejectionInsightsAPI.as_view()),
    path("dashboard/rejection-rate/", RejectionRateAPI.as_view()),
    path("dashboard/export/", ExportInfluencersAPI.as_view()),
    path("dashboard/async-report/", AsyncReportAPI.as_view()),
    path(
        "dashboard/report-status/<int:report_id>/", ReportStatusAPI.as_view()
    ),
    # influencer document
    path("upload-document/", UploadDocumentAPI.as_view()),
    path("documents/<int:influencer_id>/", InfluencerDocumentsAPI.as_view()),
    path("verify-document/<int:doc_id>/", VerifyDocumentAPI.as_view()),
    # influencer review
    path(
        "influencer-review/<int:influencer_id>/", InfluencerReviewAPI.as_view()
    ),
    # my report
    path(
        "reports/",
        MyReportsAPI.as_view(),
        name="my-reports",
    ),
    path(
        "reports/<uuid:report_id>/download/",
        DownloadReportAPI.as_view(),
        name="download-report",
    ),
    path(
        "reports/<uuid:report_id>/retry/",
        RetryReportAPI.as_view(),
        name="retry-report",
    ),
    path(
        "reports/statistics/",
        ReportStatisticsAPI.as_view(),
        name="report-statistics",
    ),
    path(
        "reports/<uuid:report_id>/secure-download/",
        SecureReportDownloadAPI.as_view(),
        name="secure-report-download",
    ),
    # Notification service
    path(
        "",
        NotificationListAPI.as_view(),
        name="notification-list",
    ),
    path(
        "<uuid:notification_id>/",
        NotificationDetailAPI.as_view(),
        name="notification-detail",
    ),
    path(
        "<uuid:notification_id>/read/",
        MarkNotificationReadAPI.as_view(),
        name="notification-read",
    ),
    path(
        "read-all/",
        MarkAllNotificationsReadAPI.as_view(),
        name="notification-read-all",
    ),
    path(
        "<uuid:notification_id>/delete/",
        DeleteNotificationAPI.as_view(),
        name="notification-delete",
    ),
    path(
        "unread-count/",
        UnreadNotificationCountAPI.as_view(),
        name="notification-unread-count",
    ),
    path(
        "preferences/",
        NotificationPreferenceAPI.as_view(),
        name="notification-preferences",
    ),
    # Bulk notification
    path(
        "bulk-notifications/",
        BulkNotificationListAPIView.as_view(),
        name="bulk-notification-list",
    ),
    path(
        "bulk-notifications/create/",
        BulkNotificationCreateAPIView.as_view(),
        name="bulk-notification-create",
    ),
    path(
        "bulk-notifications/<uuid:bulk_notification_id>/",
        BulkNotificationDetailAPIView.as_view(),
        name="bulk-notification-detail",
    ),
]"""
