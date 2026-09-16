import os
from datetime import timedelta
from pathlib import Path

from celery.schedules import crontab
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Read environment from Docker/container.
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")

# Load the corresponding environment file when it exists.
env_path = BASE_DIR / f".env.{ENVIRONMENT}"

if env_path.exists():
    load_dotenv(env_path)


SECRET_KEY = os.getenv("SECRET_KEY")


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.users",
    "apps.influencers",
    "storages",
    "apps.notifications",
]


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.middleware.RequestLoggingMiddleware",
]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST"),
        "PORT": os.getenv("DB_PORT"),
    },
}


AUTH_USER_MODEL = "users.User"

ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": (
        "rest_framework.pagination.PageNumberPagination"
    ),
    "PAGE_SIZE": 10,
    "EXCEPTION_HANDLER": "core.exception_handler.custom_exception_handler",
}


# ---------------------------------------------------------------------------
# JWT Authentication
# ---------------------------------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = "redis://redis:6379/0"

CELERY_RESULT_BACKEND = "redis://redis:6379/0"

CELERY_ACCEPT_CONTENT = ["json"]

CELERY_TASK_SERIALIZER = "json"

CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = "Asia/Kolkata"

CELERY_TASK_TRACK_STARTED = True

CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BEAT_SCHEDULE = {
    "cleanup-old-reports": {
        "task": "apps.influencers.tasks.cleanup_old_reports",
        "schedule": crontab(
            hour=2,
            minute=0,
        ),
    },
}


# ---------------------------------------------------------------------------
# AWS
# ---------------------------------------------------------------------------

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")

AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

AWS_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

AWS_REGION = os.getenv("AWS_S3_REGION_NAME")


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


# ---------------------------------------------------------------------------
# Media files
# ---------------------------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_DIR = BASE_DIR / "logs"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "app.log"),
        },
    },
    "root": {
        "handlers": [
            "console",
            "file",
        ],
        "level": "INFO",
    },
}


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST")

EMAIL_PORT = int(
    os.getenv("EMAIL_PORT", "587"),
)

EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
