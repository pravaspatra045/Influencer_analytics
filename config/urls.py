from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from core.health import health_check, readiness_check

urlpatterns = [
    # ============================================================
    # Health / Readiness
    # ============================================================
    path("healthz/", health_check, name="health-check"),
    path("readiness/", readiness_check, name="readiness-check"),
    # ============================================================
    # Admin
    # ============================================================
    path("admin/", admin.site.urls),
    # ============================================================
    # API
    # ============================================================
    path("api/v1/", include("api.v1.urls")),
    # ============================================================
    # API Documentation
    # ============================================================
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


urlpatterns += static(
    settings.STATIC_URL,
    document_root=settings.STATIC_ROOT,
)

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT,
)
