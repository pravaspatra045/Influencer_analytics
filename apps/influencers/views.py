import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from core.utils import standard_response
from apps.influencers.serializers import InfluencerRegistrationSerializer
from services.influencer_service import InfluencerService
from apps.influencers.models import Influencer
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from apps.influencers.serializers import InfluencerListSerializer,ReportListSerializer
from django.db.models import Avg, Max, Min, F, ExpressionWrapper, DurationField
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count
from apps.influencers.tasks import generate_influencer_report
from apps.influencers.models import Report ,InfluencerDocument
from services.influencer_query_service import InfluencerQueryService
from services.report_service import ReportService
#from core.pagination import StandardResultsSetPagination


logger = logging.getLogger(__name__)


class InfluencerRegistrationAPI(APIView):

    def post(self, request):
        """
        API to register influencer
        """

        serializer = InfluencerRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            try:
                influencer = InfluencerService.register_influencer(
                    serializer.validated_data
                )

                return Response(
                    standard_response(
                        message="Registration successful",
                        data={"influencer_id": str(influencer.influencer_id)},
                        status=201
                    ),
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                logger.error(f"Registration API error | {str(e)}", exc_info=True)

                return Response(
                    standard_response(
                        message="Registration failed",
                        error=str(e),
                        status=500
                    ),
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        #  Validation errors
        logger.warning(f"Validation failed | errors={serializer.errors}")

        return Response(
            standard_response(
                message="Validation error",
                error=serializer.errors,
                status=400
            ),
            status=status.HTTP_400_BAD_REQUEST
        )
    


class InfluencerApprovalAPI(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request, pk):
        """
        Approve / Reject / Hold influencer (admin/manager only)
        """

        try:
            influencer = Influencer.objects.get(pk=pk)

            status_value = request.data.get("status")
            reason = request.data.get("reason")

            InfluencerService.update_status(
                influencer,
                status_value,
                reason,
                updated_by=request.user  #  real user
            )

            return Response(
                standard_response(
                    message="Status updated successfully",
                    data={"status": status_value},
                    status=200
                ),
                status=status.HTTP_200_OK
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(
                    message="Influencer not found",
                    error="Invalid ID",
                    status=404
                ),
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Approval error | {str(e)}", exc_info=True)

            return Response(
                standard_response(
                    message="Status update failed",
                    error=str(e),
                    status=400
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
            


class InfluencerListAPI(APIView):
    """
    List influencers with filtering, searching and ordering.
    """

    permission_classes = [
        IsAuthenticated,
        
    ]

    def get(self, request):

        filters = {
            "status": request.query_params.get("status"),
            "search": request.query_params.get("search"),
            "ordering": request.query_params.get("ordering"),
            "min_followers": request.query_params.get("min_followers"),
            "max_followers": request.query_params.get("max_followers"),
        }

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
            ),
            status=status.HTTP_200_OK,
        )
    


class MyProfileAPI(APIView):
    """
    Influencer dashboard → own data
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            influencer = Influencer.objects.get(user=request.user)

            data = {
                "influencer_id": str(influencer.influencer_id),
                "status": influencer.status,
                "approved_at": influencer.approved_at,
                "rejection_reason": influencer.rejection_reason,
            }

            return Response(
                standard_response(
                    message="Profile fetched successfully",
                    data=data,
                    status=200
                )
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(
                    message="Influencer not found",
                    error="User not registered as influencer",
                    status=404
                ),
                status=404
            )
            
from core.utils import get_date_range


class DashboardStatsAPI(APIView):
    """
    Advanced dashboard stats with time filters & KPIs
    """

    permission_classes = [IsAuthenticated,]

    def get(self, request):

        range_param = request.query_params.get("range")  # 7d / 30d
        start_date = get_date_range(range_param)

        queryset = Influencer.objects.all()

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        total = queryset.count()
        approved = queryset.filter(status="approved").count()
        pending = queryset.filter(status="pending").count()
        rejected = queryset.filter(status="rejected").count()
        on_hold = queryset.filter(status="on_hold").count()

        # KPI: approval rate
        approval_rate = (approved / total * 100) if total > 0 else 0

        data = {
            "total": total,
            "approved": approved,
            "pending": pending,
            "rejected": rejected,
            "on_hold": on_hold,
            "approval_rate": round(approval_rate, 2)
        }

        return Response(
            standard_response(
                message="Dashboard stats fetched",
                data=data,
                status=200
            )
        )
        
class RecentInfluencersAPI(APIView):
    """
    Returns latest registered influencers
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        influencers = Influencer.objects.select_related('user').order_by('-created_at')[:5]

        data = [
            {
                "id": i.id,
                "email": i.user.email,
                "status": i.status,
                "created_at": i.created_at,
            }
            for i in influencers
        ]

        return Response(
            standard_response(
                message="Recent influencers fetched",
                data=data,
                status=200
            )
        )

class RecentInfluencersAPI(APIView):
    """
    Returns latest registered influencers
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        influencers = Influencer.objects.select_related('user').order_by('-created_at')[:5]

        data = [
            {
                "id": i.id,
                "email": i.user.email,
                "status": i.status,
                "created_at": i.created_at,
            }
            for i in influencers
        ]

        return Response(
            standard_response(
                message="Recent influencers fetched",
                data=data,
                status=200
            )
        )


class InfluencerTrendAPI(APIView):
    """
    Trend with time filter
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        range_param = request.query_params.get("range")
        start_date = get_date_range(range_param)

        queryset = Influencer.objects.all()

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        trends = (
            queryset
            .annotate(date=TruncDate('created_at'))
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date')
        )

        return Response(
            standard_response(
                message="Trend data fetched",
                data=list(trends)
            )
        )
        
        
        
class StatusDistributionAPI(APIView):
    """
    Returns status distribution for charts
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        distribution = (
            Influencer.objects
            .values('status')
            .annotate(count=Count('id'))
        )

        return Response(
            standard_response(
                message="Status distribution fetched",
                data=list(distribution),
                status=200
            )
        )
        
class GrowthRateAPI(APIView):
    """
    Calculates growth % between two periods
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        range_param = request.query_params.get("range", "7d")
        current_start = get_date_range(range_param)

        if not current_start:
            return Response(
                standard_response(error="Invalid range"),
                status=400
            )

        previous_start = current_start - (timezone.now() - current_start)

        current_count = Influencer.objects.filter(
            created_at__gte=current_start
        ).count()

        previous_count = Influencer.objects.filter(
            created_at__gte=previous_start,
            created_at__lt=current_start
        ).count()

        if previous_count == 0:
            growth_rate = 100 if current_count > 0 else 0
        else:
            growth_rate = ((current_count - previous_count) / previous_count) * 100

        return Response(
            standard_response(
                message="Growth rate calculated",
                data={
                    "current": current_count,
                    "previous": previous_count,
                    "growth_rate": round(growth_rate, 2)
                }
            )
        )
        
class ApprovalTimeAnalyticsAPI(APIView):
    """
    Calculates approval time metrics
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        queryset = Influencer.objects.filter(
            status='approved',
            approved_at__isnull=False
        )

        #  Calculate time difference
        queryset = queryset.annotate(
            approval_time=ExpressionWrapper(
                F('approved_at') - F('created_at'),
                output_field=DurationField()
            )
        )

        stats = queryset.aggregate(
            avg_time=Avg('approval_time'),
            max_time=Max('approval_time'),
            min_time=Min('approval_time')
        )

        # Convert duration to readable format (seconds)
        def format_duration(duration):
            return duration.total_seconds() if duration else 0

        data = {
            "average_approval_time_seconds": format_duration(stats["avg_time"]),
            "max_approval_time_seconds": format_duration(stats["max_time"]),
            "min_approval_time_seconds": format_duration(stats["min_time"]),
        }

        return Response(
            standard_response(
                message="Approval time analytics fetched",
                data=data
            )
        )
        
class RejectionInsightsAPI(APIView):
    """
    Analyze rejection reasons
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        queryset = Influencer.objects.filter(status='rejected')

        # 🔥 Group by rejection reason
        data = (
            queryset
            .values('rejection_reason')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        total_rejected = queryset.count()

        return Response(
            standard_response(
                message="Rejection insights fetched",
                data={
                    "total_rejected": total_rejected,
                    "reasons": list(data)
                }
            )
        )
        
class RejectionRateAPI(APIView):
    """
    Calculate rejection percentage
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request):

        total = Influencer.objects.count()
        rejected = Influencer.objects.filter(status='rejected').count()

        rejection_rate = (rejected / total * 100) if total > 0 else 0

        return Response(
            standard_response(
                message="Rejection rate calculated",
                data={
                    "total": total,
                    "rejected": rejected,
                    "rejection_rate": round(rejection_rate, 2)
                }
            )
        )
        
from django.http import HttpResponse
from services.report_service import ReportService


class ExportInfluencersAPI(APIView):
    """
    Export Influencers.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        filters = {
            "status": request.query_params.get("status"),
            "search": request.query_params.get("search"),
            "ordering": request.query_params.get("ordering"),
            "min_followers": request.query_params.get("min_followers"),
            "max_followers": request.query_params.get("max_followers"),
        }

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

            response[
                "Content-Disposition"
            ] = (
                f'attachment; filename="{export_data["filename"]}"'
            )

            return response

        except ValueError:

            return Response(
                standard_response(
                    error="Invalid export format."
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )
        
from apps.influencers.services import create_export_report

class AsyncReportAPI(APIView):

    permission_classes = [IsAuthenticated, ]

    def post(self, request):

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
            ),
            status=status.HTTP_202_ACCEPTED,
        )
        
        
from apps.influencers.models import ExportReport
class ReportStatusAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):

        try:

            report = ExportReport.objects.get(id=report_id)

            return Response(
                standard_response(
                    message="Report status fetched.",
                    data={
                        "report_id": str(report.id),
                        "status": report.status,
                        "file_url": report.file.url if report.file else None,
                        "error": report.error_message,
                    },
                )
            )

        except ExportReport.DoesNotExist:

            return Response(
                standard_response(
                    error="Report not found.",
                ),
                status=status.HTTP_404_NOT_FOUND,
            )
from services.storage_service import StorageService     
    
class UploadDocumentAPI(APIView):
    """
    Upload influencer KYC documents
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        try:
            influencer = Influencer.objects.get(user=request.user)

            document_type = request.data.get("document_type")
            file = request.FILES.get("file")

            if not file:
                return Response(
                    standard_response(error="File is required"),
                    status=400
                )

            # 🔹 Upload to S3
            file_url = StorageService.upload_file(file)

            # 🔹 Save document
            InfluencerDocument.objects.create(
                influencer=influencer,
                document_type=document_type,
                file_url=file_url
            )

            return Response(
                standard_response(
                    message="Document uploaded successfully",
                    data={"file_url": file_url}
                )
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(error="Influencer not found"),
                status=404
            )
            

class InfluencerDocumentsAPI(APIView):
    """
    Admin view influencer documents
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request, influencer_id):

        documents = InfluencerDocument.objects.filter(
            influencer_id=influencer_id
        )

        data = [
            {
                "type": doc.document_type,
                "url": doc.file_url,
                "verified": doc.is_verified
            }
            for doc in documents
        ]

        return Response(
            standard_response(
                message="Documents fetched",
                data=data
            )
        )
        
class VerifyDocumentAPI(APIView):
    """
    Admin verifies documents
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, doc_id):

        try:
            doc = InfluencerDocument.objects.get(id=doc_id)

            doc.is_verified = True
            doc.save()

            return Response(
                standard_response(message="Document verified")
            )

        except InfluencerDocument.DoesNotExist:
            return Response(
                standard_response(error="Document not found"),
                status=404
            )
            

class InfluencerReviewAPI(APIView):
    """
    Admin full review API
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request, influencer_id):

        try:
            influencer = Influencer.objects.select_related(
                "user", "influencerprofile", "bankdetail"
            ).get(id=influencer_id)

            # 🔹 Profile completion
            completion = InfluencerService.calculate_profile_completion(influencer)

            # 🔹 Documents
            documents = influencer.documents.all()
            docs_data = [
                {
                    "type": d.document_type,
                    "url": d.file_url,
                    "verified": d.is_verified
                }
                for d in documents
            ]

            # 🔹 Social media
            socials = influencer.socialmediaaccount_set.all()
            social_data = [
                {
                    "platform": s.platform,
                    "handle": s.handle,
                    "followers": s.followers
                }
                for s in socials
            ]

            data = {
                "id": influencer.id,
                "email": influencer.user.email,
                "status": influencer.status,

                "profile_completion": completion,

                "profile": {
                    "full_name": influencer.influencerprofile.full_name,
                    "phone": influencer.influencerprofile.phone,
                },

                "bank": {
                    "account_number": influencer.bankdetail.account_number,
                    "bank_name": influencer.bankdetail.bank_name,
                },

                "documents": docs_data,
                "social_media": social_data,
            }

            return Response(
                standard_response(
                    message="Influencer details fetched",
                    data=data
                )
            )

        except Influencer.DoesNotExist:
            return Response(
                standard_response(error="Influencer not found"),
                status=404
            )

from core.pagination import StandardPagination
from apps.influencers.serializers import (
    ReportListSerializer,
)


class MyReportsAPI(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

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
            context={
                "request": request,
            },
        )

        return paginator.get_paginated_response(
            standard_response(
                message="Reports fetched successfully.",
                data=serializer.data,
            )
        )


from django.http import FileResponse


class DownloadReportAPI(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, report_id):

        report = ReportService.get_report_for_download(
            report_id,
            request.user
        )

        if report.status == ExportReport.Status.PROCESSING:

            return Response(
                standard_response(
                    error="Report is still processing."
                ),
                status=202
            )

        if report.status == ExportReport.Status.FAILED:

            return Response(
                standard_response(
                    error="Report generation failed."
                ),
                status=400
            )

        if not report.file:

            return Response(
                standard_response(
                    error="Report file not found."
                ),
                status=404
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

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, report_id):
        """
        Retry a failed report.
        """

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
                ),
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:

            return Response(
                standard_response(
                    error=str(exc),
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )
            

class ReportStatisticsAPI(APIView):
    """
    Report statistics.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        data = ReportService.get_report_statistics(
            request.user
        )

        return Response(
            standard_response(
                message="Statistics fetched successfully.",
                data=data,
            ),
            status=status.HTTP_200_OK,
        )
        
class SecureReportDownloadAPI(APIView):
    """
    Generate a temporary download URL for a report.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, report_id):

        report = ReportService.get_report_for_download(
            report_id=report_id,
            user=request.user,
        )

        if not report.file:
            return Response(
                standard_response(
                    error="Report file not found."
                ),
                status=status.HTTP_404_NOT_FOUND,
            )

        url = StorageService.generate_presigned_url(
            report.file.name
        )

        return Response(
            standard_response(
                message="Download URL generated successfully.",
                data={
                    "download_url": url,
                    "expires_in": 600,
                },
            ),
            status=status.HTTP_200_OK,
        )