import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import LoginSerializer
from core.utils import standard_response

logger = logging.getLogger(__name__)


class LoginAPI(APIView):
    """
    Authenticate a user and return JWT access/refresh tokens.

    Request:
        POST /login/

    Response:
        {
            "message": "Login successful",
            "data": {
                "access": "...",
                "refresh": "...",
                "role": "ADMIN"
            }
        }
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def post(self, request: Request) -> Response:
        """
        Authenticate user credentials and return JWT tokens.
        """

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            logger.info(
                "User login successful | user_id=%s",
                user.id,
            )

            return Response(
                standard_response(
                    message="Login successful",
                    data={
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "role": user.role,
                    },
                    status=status.HTTP_200_OK,
                ),
                status=status.HTTP_200_OK,
            )

        except Exception:
            logger.exception("Unexpected error during login.")
            raise
