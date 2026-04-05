from rest_framework.permissions import BasePermission

from common.enums import UserTypeChoices


class IsDoctorOrReceptionist(BasePermission):
    message = "Only doctor or receptionist can access this endpoint."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type in [
                UserTypeChoices.DOCTOR,
                UserTypeChoices.RECEPTIONIST,
            ]
        )