from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    """
    Allow access only to admin or manager users.
    """

    message = "Admin or manager access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (
                "admin",
                "manager",
            )
        )


class IsAdmin(BasePermission):
    """
    Allow access only to admin users.
    """

    message = "Admin access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "admin"
        )


class IsInfluencer(BasePermission):
    """
    Allow access only to influencer users.
    """

    message = "Influencer access is required."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "influencer"
        )
