import logging

from django.db.models import (
    Avg,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    Max,
    Min,
)
from django.db.models.functions import TruncDate
from django.http import FileResponse, HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.influencers.models import (
    ExportReport,
    Influencer,
    InfluencerDocument,
)
from apps.influencers.serializers import (
    InfluencerListSerializer,
    InfluencerRegistrationSerializer,
    MyProfileSerializer,
    ReportListSerializer,
    UpdateMyProfileSerializer,
)
from apps.influencers.services import create_export_report
from core.pagination import StandardPagination
from core.utils import get_date_range, standard_response
from services.influencer_query_service import InfluencerQueryService
from services.influencer_service import InfluencerService
from services.media_service import MediaService
from services.profile_query_service import ProfileQueryService
from services.profile_service import ProfileService
from services.report_service import (
    InvalidExportFormatError,
    ReportRetryError,
    ReportService,
)
from services.storage_service import StorageService

logger = logging.getLogger(__name__)


def _get_influencer_filters(request: Request) -> dict:
    """
    Extract supported influencer filters from request query parameters.
    """

    return {
        "status": request.query_params.get("status"),
        "search": request.query_params.get("search"),
        "ordering": request.query_params.get("ordering"),
        "min_followers": request.query_params.get("min_followers"),
        "max_followers": request.query_params.get("max_followers"),
    }


class InfluencerRegistrationAPI(APIView):
    """
    Register a new influencer.
    """

    def post(self, request: Request) -> Response:
        serializer = InfluencerRegistrationSerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            logger.warning(
                "Influencer registration validation failed | errors=%s",
                serializer.errors,
            )

            return Response(
                standard_response(
                    message="Validation error",
                    error=serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            influencer = InfluencerService.register_influencer(
                serializer.validated_data,
            )

            return Response(
                standard_response(
                    message="Registration successful",
                    data={
                        "influencer_id": str(influencer.influencer_id),
                    },
                    status=status.HTTP_201_CREATED,
                ),
                status=status.HTTP_201_CREATED,
            )

        except Exception as exc:
            logger.exception(
                "Influencer registration API failed | error=%s",
                exc,
            )

            return Response(
                standard_response(
                    message="Registration failed",
                    error=str(exc),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InfluencerApprovalAPI(APIView):
    """
    Approve, reject, or put an influencer on hold.

    Authorization is currently preserved as authenticated-user access.
    Role-specific authorization can be hardened in the security phase.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, pk: int) -> Response:
        try:
            influencer = Influencer.objects.get(pk=pk)

            status_value = request.data.get("status")
            reason = request.data.get("reason")

            InfluencerService.update_status(
                influencer=influencer,
                status=status_value,
                reason=reason,
                updated_by=request.user,
            )

            return Response(
                standard_response(
                    message="Status updated successfully",
                    data={
                        "status": status_value,
                    },
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(
                    message="Influencer not found",
                    error="Invalid ID",
                    status=status.HTTP_404_NOT_FOUND,
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as exc:
            logger.exception(
                "Influencer approval API failed | influencer_id=%s | error=%s",
                pk,
                exc,
            )

            return Response(
                standard_response(
                    message="Status update failed",
                    error=str(exc),
                    status=status.HTTP_400_BAD_REQUEST,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )


class InfluencerListAPI(APIView):
    """
    List influencers with filtering, searching, and ordering.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        filters = _get_influencer_filters(request)

        queryset = InfluencerQueryService.get_queryset(filters)

        serializer = InfluencerListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )

        return Response(
            standard_response(
                message="Influencers fetched successfully.",
                data=serializer.data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class MyProfileAPI(APIView):
    """
    Get the authenticated influencer's profile.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        influencer = ProfileQueryService.get_my_profile(
            request.user,
        )

        serializer = MyProfileSerializer(
            influencer,
            context={"request": request},
        )

        return Response(
            standard_response(
                message="Profile fetched successfully",
                data=serializer.data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class DashboardStatsAPI(APIView):
    """
    Return dashboard statistics with optional time filtering.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        range_param = request.query_params.get("range")
        start_date = get_date_range(range_param)

        queryset = Influencer.objects.all()

        if start_date:
            queryset = queryset.filter(
                created_at__gte=start_date,
            )

        total = queryset.count()
        approved = queryset.filter(
            status=Influencer.Status.APPROVED,
        ).count()
        pending = queryset.filter(
            status=Influencer.Status.PENDING,
        ).count()
        rejected = queryset.filter(
            status=Influencer.Status.REJECTED,
        ).count()
        on_hold = queryset.filter(
            status=Influencer.Status.ON_HOLD,
        ).count()

        approval_rate = approved / total * 100 if total > 0 else 0

        data = {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
            "on_hold": on_hold,
            "approval_rate": round(approval_rate, 2),
        }

        return Response(
            standard_response(
                message="Dashboard stats fetched",
                data=data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class RecentInfluencersAPI(APIView):
    """
    Return the latest registered influencers.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        influencers = Influencer.objects.select_related("user").order_by(
            "-created_at"
        )[:5]

        data = [
            {
                "id": influencer.id,
                "email": influencer.user.email,
                "status": influencer.status,
                "created_at": influencer.created_at,
            }
            for influencer in influencers
        ]

        return Response(
            standard_response(
                message="Recent influencers fetched",
                data=data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class InfluencerTrendAPI(APIView):
    """
    Return influencer registration trends grouped by date.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        range_param = request.query_params.get("range")
        start_date = get_date_range(range_param)

        queryset = Influencer.objects.all()

        if start_date:
            queryset = queryset.filter(
                created_at__gte=start_date,
            )

        trends = (
            queryset.annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        return Response(
            standard_response(
                message="Trend data fetched",
                data=list(trends),
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class StatusDistributionAPI(APIView):
    """
    Return influencer status distribution for charts.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        distribution = Influencer.objects.values("status").annotate(
            count=Count("id")
        )

        return Response(
            standard_response(
                message="Status distribution fetched",
                data=list(distribution),
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class GrowthRateAPI(APIView):
    """
    Calculate influencer growth percentage between two periods.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        range_param = request.query_params.get("range", "7d")
        current_start = get_date_range(range_param)

        if not current_start:
            return Response(
                standard_response(
                    error="Invalid range",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()
        period_duration = now - current_start
        previous_start = current_start - period_duration

        current_count = Influencer.objects.filter(
            created_at__gte=current_start,
        ).count()

        previous_count = Influencer.objects.filter(
            created_at__gte=previous_start,
            created_at__lt=current_start,
        ).count()

        if previous_count == 0:
            growth_rate = 100 if current_count > 0 else 0
        else:
            growth_rate = (
                (current_count - previous_count) / previous_count
            ) * 100

        return Response(
            standard_response(
                message="Growth rate calculated",
                data={
                    "current": current_count,
                    "previous": previous_count,
                    "growth_rate": round(growth_rate, 2),
                },
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class ApprovalTimeAnalyticsAPI(APIView):
    """
    Calculate approval-time metrics.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        queryset = Influencer.objects.filter(
            status=Influencer.Status.APPROVED,
            approved_at__isnull=False,
        ).annotate(
            approval_time=ExpressionWrapper(
                F("approved_at") - F("created_at"),
                output_field=DurationField(),
            ),
        )

        stats = queryset.aggregate(
            avg_time=Avg("approval_time"),
            max_time=Max("approval_time"),
            min_time=Min("approval_time"),
        )

        def format_duration(duration):
            return duration.total_seconds() if duration else 0

        data = {
            "average_approval_time_seconds": format_duration(
                stats["avg_time"],
            ),
            "max_approval_time_seconds": format_duration(
                stats["max_time"],
            ),
            "min_approval_time_seconds": format_duration(
                stats["min_time"],
            ),
        }

        return Response(
            standard_response(
                message="Approval time analytics fetched",
                data=data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class RejectionInsightsAPI(APIView):
    """
    Analyze influencer rejection reasons.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        queryset = Influencer.objects.filter(
            status=Influencer.Status.REJECTED,
        )

        data = (
            queryset.values("rejection_reason")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        total_rejected = queryset.count()

        return Response(
            standard_response(
                message="Rejection insights fetched",
                data={
                    "total_rejected": total_rejected,
                    "reasons": list(data),
                },
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class RejectionRateAPI(APIView):
    """
    Calculate the overall influencer rejection percentage.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        total = Influencer.objects.count()

        rejected = Influencer.objects.filter(
            status=Influencer.Status.REJECTED,
        ).count()

        rejection_rate = rejected / total * 100 if total > 0 else 0

        return Response(
            standard_response(
                message="Rejection rate calculated",
                data={
                    "total": total,
                    "rejected": rejected,
                    "rejection_rate": round(rejection_rate, 2),
                },
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class ExportInfluencersAPI(APIView):
    """
    Export influencers using the synchronous report service.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> HttpResponse | Response:
        filters = _get_influencer_filters(request)

        export_format = request.query_params.get(
            "format",
            "csv",
        )

        try:
            export_data = ReportService.export_report(
                filters=filters,
                export_format=export_format,
            )

            response = HttpResponse(
                export_data["buffer"],
                content_type=export_data["content_type"],
            )

            response["Content-Disposition"] = (
                f'attachment; filename="{export_data["filename"]}"'
            )

            return response

        except InvalidExportFormatError:
            return Response(
                standard_response(
                    error="Invalid export format.",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )


class AsyncReportAPI(APIView):
    """
    Start asynchronous influencer report generation.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        filters = {
            "status": request.data.get("status"),
            "search": request.data.get("search"),
            "ordering": request.data.get("ordering"),
            "min_followers": request.data.get("min_followers"),
            "max_followers": request.data.get("max_followers"),
        }

        report = create_export_report(
            request.user,
            filters=filters,
        )

        return Response(
            standard_response(
                message="Report generation started.",
                data={
                    "report_id": str(report.id),
                    "status": report.status,
                },
                status=status.HTTP_202_ACCEPTED,
            ),
            status=status.HTTP_202_ACCEPTED,
        )


class ReportStatusAPI(APIView):
    """
    Return the status of an asynchronous report.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request, report_id) -> Response:
        try:
            report = ExportReport.objects.get(
                id=report_id,
            )

            return Response(
                standard_response(
                    message="Report status fetched.",
                    data={
                        "report_id": str(report.id),
                        "status": report.status,
                        "file_url": (report.file.url if report.file else None),
                        "error": report.error_message,
                    },
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except ExportReport.DoesNotExist:
            return Response(
                standard_response(
                    error="Report not found.",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )


class UploadDocumentAPI(APIView):
    """
    Upload an influencer KYC document.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        try:
            influencer = Influencer.objects.get(
                user=request.user,
            )

            document_type = request.data.get(
                "document_type",
            )
            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                return Response(
                    standard_response(
                        error="File is required",
                    ),
                    status=status.HTTP_400_BAD_REQUEST,
                )

            file_url = StorageService.upload_file(
                uploaded_file,
            )

            InfluencerDocument.objects.create(
                influencer=influencer,
                document_type=document_type,
                file_url=file_url,
            )

            return Response(
                standard_response(
                    message="Document uploaded successfully",
                    data={
                        "file_url": file_url,
                    },
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(
                    error="Influencer not found",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )


class InfluencerDocumentsAPI(APIView):
    """
    Return documents belonging to an influencer.
    """

    permission_classes = (IsAuthenticated,)

    def get(
        self,
        request: Request,
        influencer_id,
    ) -> Response:
        documents = InfluencerDocument.objects.filter(
            influencer_id=influencer_id,
        )

        data = [
            {
                "type": document.document_type,
                "url": document.file_url,
                "verified": document.is_verified,
            }
            for document in documents
        ]

        return Response(
            standard_response(
                message="Documents fetched",
                data=data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class VerifyDocumentAPI(APIView):
    """
    Mark an influencer document as verified.
    """

    permission_classes = (IsAuthenticated,)

    def post(
        self,
        request: Request,
        doc_id,
    ) -> Response:
        try:
            document = InfluencerDocument.objects.get(
                id=doc_id,
            )

            document.is_verified = True
            document.save(
                update_fields=("is_verified",),
            )

            return Response(
                standard_response(
                    message="Document verified",
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except InfluencerDocument.DoesNotExist:
            return Response(
                standard_response(
                    error="Document not found",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )


class InfluencerReviewAPI(APIView):
    """
    Return complete influencer review information.
    """

    permission_classes = (IsAuthenticated,)

    def get(
        self,
        request: Request,
        influencer_id,
    ) -> Response:
        try:
            influencer = (
                Influencer.objects.select_related(
                    "user",
                    "profile",
                    "bank_detail",
                )
                .prefetch_related(
                    "documents",
                    "social_accounts",
                )
                .get(id=influencer_id)
            )

            completion = InfluencerService.calculate_profile_completion(
                influencer,
            )

            documents = influencer.documents.all()

            documents_data = [
                {
                    "type": document.document_type,
                    "url": document.file_url,
                    "verified": document.is_verified,
                }
                for document in documents
            ]

            social_accounts = influencer.social_accounts.all()

            social_data = [
                {
                    "platform": account.platform,
                    "handle": account.handle,
                    "followers": account.followers,
                }
                for account in social_accounts
            ]

            data = {
                "id": influencer.id,
                "email": influencer.user.email,
                "status": influencer.status,
                "profile_completion": completion,
                "profile": {
                    "full_name": influencer.profile.full_name,
                    "phone": influencer.profile.phone,
                },
                "bank": {
                    "account_number": influencer.bank_detail.account_number,
                    "bank_name": influencer.bank_detail.bank_name,
                },
                "documents": documents_data,
                "social_media": social_data,
            }

            return Response(
                standard_response(
                    message="Influencer details fetched",
                    data=data,
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(
                    error="Influencer not found",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )


class MyReportsAPI(APIView):
    """
    Return paginated reports belonging to the authenticated user.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        queryset = ReportService.get_reports(
            request.user,
            request.query_params,
        )

        paginator = StandardPagination()

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = ReportListSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(
            standard_response(
                message="Reports fetched successfully.",
                data=serializer.data,
                status=status.HTTP_200_OK,
            ),
        )


class DownloadReportAPI(APIView):
    """
    Download a generated report.
    """

    permission_classes = (IsAuthenticated,)

    def get(
        self,
        request: Request,
        report_id,
    ):
        report = ReportService.get_report_for_download(
            report_id,
            request.user,
        )

        if report.status == ExportReport.Status.PROCESSING:
            return Response(
                standard_response(
                    error="Report is still processing.",
                ),
                status=status.HTTP_202_ACCEPTED,
            )

        if report.status == ExportReport.Status.FAILED:
            return Response(
                standard_response(
                    error="Report generation failed.",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not report.file:
            return Response(
                standard_response(
                    error="Report file not found.",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            report.file.open("rb"),
            as_attachment=True,
            filename=report.file.name.split("/")[-1],
        )


class RetryReportAPI(APIView):
    """
    Retry a failed report.
    """

    permission_classes = (IsAuthenticated,)

    def post(
        self,
        request: Request,
        report_id,
    ) -> Response:
        try:
            report = ReportService.retry_report(
                report_id=report_id,
                user=request.user,
            )

            return Response(
                standard_response(
                    message="Report queued successfully.",
                    data={
                        "report_id": str(report.id),
                        "task_id": report.task_id,
                        "status": report.status,
                    },
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except ReportRetryError as exc:
            return Response(
                standard_response(
                    error=str(exc),
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReportStatisticsAPI(APIView):
    """
    Return report statistics for the authenticated user.
    """

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        data = ReportService.get_report_statistics(
            request.user,
        )

        return Response(
            standard_response(
                message="Statistics fetched successfully.",
                data=data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class SecureReportDownloadAPI(APIView):
    """
    Generate a temporary report download URL.
    """

    permission_classes = (IsAuthenticated,)

    def get(
        self,
        request: Request,
        report_id,
    ) -> Response:
        report = ReportService.get_report_for_download(
            report_id=report_id,
            user=request.user,
        )

        if not report.file:
            return Response(
                standard_response(
                    error="Report file not found.",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        url = StorageService.generate_presigned_url(
            report.file.name,
        )

        return Response(
            standard_response(
                message="Download URL generated successfully.",
                data={
                    "download_url": url,
                    "expires_in": 600,
                },
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class UpdateMyProfileAPI(APIView):
    """
    Update the authenticated influencer profile.
    """

    permission_classes = (IsAuthenticated,)

    def put(self, request: Request) -> Response:
        influencer = ProfileQueryService.get_my_profile(
            request.user,
        )

        serializer = UpdateMyProfileSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        ProfileService.update_profile(
            influencer=influencer,
            profile_data=serializer.validated_data.get(
                "profile",
                {},
            ),
            bank_data=serializer.validated_data.get(
                "bank_detail",
            ),
            social_accounts=serializer.validated_data.get(
                "social_accounts",
            ),
        )

        influencer = ProfileQueryService.get_my_profile(
            request.user,
        )

        return Response(
            standard_response(
                message="Profile updated successfully.",
                data=MyProfileSerializer(
                    influencer,
                    context={"request": request},
                ).data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class UploadProfileImageAPI(APIView):
    """
    Upload an influencer profile image.
    """

    permission_classes = (IsAuthenticated,)

    parser_classes = (
        MultiPartParser,
        FormParser,
    )

    def patch(self, request: Request) -> Response:
        if "profile_image" not in request.FILES:
            return Response(
                standard_response(
                    error="Profile image is required.",
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        influencer = ProfileQueryService.get_my_profile(
            request.user,
        )

        MediaService.upload_profile_image(
            influencer,
            request.FILES["profile_image"],
        )

        influencer.refresh_from_db()

        serializer = MyProfileSerializer(
            influencer,
            context={"request": request},
        )

        return Response(
            standard_response(
                message="Profile image uploaded successfully.",
                data=serializer.data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )


class DeleteProfileImageAPI(APIView):
    """
    Delete the authenticated influencer's profile image.
    """

    permission_classes = (IsAuthenticated,)

    def delete(self, request: Request) -> Response:
        influencer = ProfileQueryService.get_my_profile(
            request.user,
        )

        MediaService.delete_profile_image(
            influencer,
        )

        influencer.refresh_from_db()

        serializer = MyProfileSerializer(
            influencer,
            context={"request": request},
        )

        return Response(
            standard_response(
                message="Profile image deleted successfully.",
                data=serializer.data,
                status=status.HTTP_200_OK,
            ),
            status=status.HTTP_200_OK,
        )
