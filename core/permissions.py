from rest_framework.permissions import BasePermission


class IsAdminOrManager(BasePermission):
    """
    Allows only admin or manager users
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.role in ['admin', 'manager']