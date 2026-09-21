import logging

from django.core.cache import cache
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.serializers import LoginSerializer
from core.utils import standard_response

logger = logging.getLogger(__name__)


LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60


class LoginAPI(APIView):
    """
    Authenticate a user and return JWT access/refresh tokens.

    Login is protected against repeated failed authentication attempts.
    """

    permission_classes = (AllowAny,)
    authentication_classes = ()

    def _get_client_ip(self, request: Request) -> str:
        """
        Return the direct client IP.

        REMOTE_ADDR is used intentionally instead of trusting arbitrary
        X-Forwarded-For headers from clients.
        """

        return request.META.get(
            "REMOTE_ADDR",
            "unknown",
        )

    def _get_login_cache_key(
        self,
        request: Request,
    ) -> str:
        """
        Build a cache key scoped to IP + submitted username.
        """

        username = (
            str(
                request.data.get(
                    "username",
                    "",
                )
            )
            .strip()
            .lower()
        )

        client_ip = self._get_client_ip(request)

        return f"login-fail:{client_ip}:{username}"

    def _is_rate_limited(
        self,
        request: Request,
    ) -> bool:
        """
        Check whether this login identity is temporarily locked.
        """

        cache_key = self._get_login_cache_key(request)

        attempts = cache.get(
            cache_key,
            0,
        )

        return attempts >= LOGIN_MAX_ATTEMPTS

    def _record_failed_attempt(
        self,
        request: Request,
    ) -> None:
        """
        Increment the failed-login counter.
        """

        cache_key = self._get_login_cache_key(request)

        try:
            attempts = cache.incr(cache_key)

        except ValueError:
            cache.set(
                cache_key,
                1,
                timeout=LOGIN_LOCKOUT_SECONDS,
            )
            return

        if attempts == 1:
            cache.expire(
                cache_key,
                LOGIN_LOCKOUT_SECONDS,
            )

    def _clear_failed_attempts(
        self,
        request: Request,
    ) -> None:
        """
        Clear failed-login attempts after successful authentication.
        """

        cache.delete(
            self._get_login_cache_key(request),
        )

    def post(
        self,
        request: Request,
    ) -> Response:
        """
        Authenticate user credentials and return JWT tokens.
        """

        if self._is_rate_limited(request):
            logger.warning(
                "Login temporarily blocked | ip=%s",
                self._get_client_ip(request),
            )

            response = Response(
                standard_response(
                    message="Too many failed login attempts. "
                    "Please try again later.",
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                ),
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

            response["Retry-After"] = str(
                LOGIN_LOCKOUT_SECONDS,
            )

            return response

        serializer = LoginSerializer(
            data=request.data,
        )

        if not serializer.is_valid():
            self._record_failed_attempt(request)

            logger.warning(
                "Login failed | ip=%s",
                self._get_client_ip(request),
            )

            return Response(
                standard_response(
                    message="Invalid login credentials.",
                    status=status.HTTP_401_UNAUTHORIZED,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            self._clear_failed_attempts(request)

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
            logger.exception(
                "Unexpected error during login.",
            )
            raise
