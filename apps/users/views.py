import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.serializers import LoginSerializer
from core.utils import standard_response

logger = logging.getLogger(__name__)


class LoginAPI(APIView):

    def post(self, request):
        """
        Login API → returns JWT tokens
        """

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # 🔹 Generate tokens
            refresh = RefreshToken.for_user(user)

            logger.info(f"User login success | user_id={user.id}")

            return Response(
                standard_response(
                    message="Login successful",
                    data={
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                        "role": user.role
                    },
                    status=200
                ),
                status=status.HTTP_200_OK
            )

        logger.warning(f"Login failed | errors={serializer.errors}")

        return Response(
            standard_response(
                message="Login failed",
                error=serializer.errors,
                status=400
            ),
            status=status.HTTP_400_BAD_REQUEST
        )