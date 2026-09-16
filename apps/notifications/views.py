from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.serializers import (
    BulkNotificationCreateSerializer,
    BulkNotificationSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
)
from core.pagination import StandardPagination
from core.utils import standard_response
from services.bulk_notification_query_service import (
    BulkNotificationQueryService,
)
from services.bulk_notification_service import BulkNotificationService
from services.notification_preference_query_service import (
    NotificationPreferenceQueryService,
)
from services.notification_query_service import NotificationQueryService
from services.notification_service import NotificationService


class NotificationListAPI(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    pagination_class = StandardPagination

    def get(self, request):

        filters = {
            "is_read": request.query_params.get("is_read"),
            "category": request.query_params.get("category"),
            "notification_type": request.query_params.get("notification_type"),
            "search": request.query_params.get("search"),
            "ordering": request.query_params.get(
                "ordering",
                "-created_at",
            ),
        }

        # Convert string to boolean
        if filters["is_read"] is not None:

            filters["is_read"] = filters["is_read"].lower() == "true"

        queryset = NotificationQueryService.get_queryset(
            request.user,
            filters,
        )

        paginator = self.pagination_class()

        page = paginator.paginate_queryset(
            queryset,
            request,
        )

        serializer = NotificationSerializer(
            page,
            many=True,
        )

        return paginator.get_paginated_response(serializer.data)


class NotificationDetailAPI(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def get(
        self,
        request,
        notification_id,
    ):

        notification = NotificationQueryService.get_notification(
            notification_id,
            request.user,
        )

        serializer = NotificationSerializer(notification)

        return Response(
            standard_response(
                message="Notification fetched successfully.",
                data=serializer.data,
                status=200,
            )
        )


class MarkNotificationReadAPI(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(
        self,
        request,
        notification_id,
    ):

        notification = NotificationQueryService.get_notification(
            notification_id,
            request.user,
        )

        NotificationService.mark_as_read(notification)

        serializer = NotificationSerializer(notification)

        return Response(
            standard_response(
                message="Notification marked as read.",
                data=serializer.data,
                status=200,
            )
        )


class MarkAllNotificationsReadAPI(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def patch(
        self,
        request,
    ):

        NotificationService.mark_all_as_read(request.user)

        return Response(
            standard_response(
                message="All notifications marked as read.",
                status=200,
            )
        )


class DeleteNotificationAPI(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    def delete(
        self,
        request,
        notification_id,
    ):

        notification = NotificationQueryService.get_notification(
            notification_id,
            request.user,
        )

        NotificationService.delete(notification)

        return Response(
            standard_response(
                message="Notification deleted successfully.",
                status=200,
            )
        )


class UnreadNotificationCountAPI(APIView):
    """
    Returns unread notification count.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        count = NotificationQueryService.unread_count(request.user)

        return Response(
            standard_response(
                message="Unread count fetched.",
                data={
                    "unread_count": count,
                },
                status=200,
            )
        )


class NotificationPreferenceAPI(APIView):
    """
    Get/Update notification preferences.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):

        preference = NotificationPreferenceQueryService.get_or_create(
            request.user
        )

        serializer = NotificationPreferenceSerializer(preference)

        return Response(
            standard_response(
                message="Preferences fetched successfully.",
                data=serializer.data,
                status=200,
            )
        )

    def patch(self, request):

        preference = NotificationPreferenceQueryService.get_or_create(
            request.user
        )

        serializer = NotificationPreferenceSerializer(
            preference,
            data=request.data,
            partial=True,
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(
            standard_response(
                message="Preferences updated successfully.",
                data=serializer.data,
                status=200,
            )
        )


class BulkNotificationCreateAPIView(CreateAPIView):
    """
    Creates a bulk notification job.
    """

    serializer_class = BulkNotificationCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        job = BulkNotificationService.create_job(
            created_by=request.user,
            **serializer.validated_data,
        )

        return Response(
            {
                "message": "Bulk notification started.",
                "data": BulkNotificationSerializer(job).data,
            },
            status=status.HTTP_201_CREATED,
        )


class BulkNotificationListAPIView(ListAPIView):
    """
    Returns bulk notification jobs.
    """

    serializer_class = BulkNotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return BulkNotificationQueryService.get_queryset(
            self.request.user,
        )


class BulkNotificationDetailAPIView(RetrieveAPIView):
    """
    Returns a single bulk notification job.
    """

    serializer_class = BulkNotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "bulk_notification_id"

    def get_queryset(self):

        return BulkNotificationQueryService.get_queryset(
            self.request.user,
        )
