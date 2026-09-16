import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_SSL_REDIRECT = (
    os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
)

SESSION_COOKIE_SECURE = (
    os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
)
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "False").lower() == "true"

SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "False").lower() == "true"
)
SECURE_HSTS_PRELOAD = (
    os.getenv("SECURE_HSTS_PRELOAD", "False").lower() == "true"
)


# ---------------------------------------------------------------------------
# AWS S3
# ---------------------------------------------------------------------------

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_REGION")

AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
