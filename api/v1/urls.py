from django.urls import path
from apps.influencers.views import (InfluencerRegistrationAPI,InfluencerApprovalAPI,InfluencerListAPI,
    MyProfileAPI,DashboardStatsAPI,
    RecentInfluencersAPI,
    InfluencerTrendAPI,
    StatusDistributionAPI,GrowthRateAPI,ApprovalTimeAnalyticsAPI, RejectionInsightsAPI, RejectionRateAPI ,ExportInfluencersAPI, AsyncReportAPI,ReportStatusAPI
    ,UploadDocumentAPI, InfluencerDocumentsAPI, VerifyDocumentAPI, InfluencerReviewAPI)
from apps.users.views import LoginAPI


urlpatterns = [
    # Auth 
    path("login/", LoginAPI.as_view()),
    
    # influencer
    path("register/", InfluencerRegistrationAPI.as_view()),
    path("influencer/<int:pk>/status/", InfluencerApprovalAPI.as_view()),
    path("influencers-list/", InfluencerListAPI.as_view()),
    path("my-profile/", MyProfileAPI.as_view()),
    
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
    path("dashboard/report-status/<int:report_id>/", ReportStatusAPI.as_view()),
    
    # influencer document
    path("upload-document/", UploadDocumentAPI.as_view()),
    path("documents/<int:influencer_id>/", InfluencerDocumentsAPI.as_view()),
    path("verify-document/<int:doc_id>/", VerifyDocumentAPI.as_view()),
    
    # influencer review
    path("influencer-review/<int:influencer_id>/", InfluencerReviewAPI.as_view()),
]