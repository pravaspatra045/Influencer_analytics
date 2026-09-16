from rest_framework.exceptions import APIException


class BusinessException(APIException):
    status_code = 400
    default_detail = "Business validation failed."
    default_code = "business_error"


class ResourceNotFound(APIException):
    status_code = 404
    default_detail = "Resource not found."
    default_code = "not_found"


class PermissionDeniedException(APIException):
    status_code = 403
    default_detail = "Permission denied."


class ConflictException(APIException):
    status_code = 409
    default_detail = "Conflict occurred."
    default_code = "conflict"
