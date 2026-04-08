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



class IsAdmin(BasePermission):
    message = "Only admin users can access this endpoint."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type == UserTypeChoices.ADMIN
        )


class IsAdminOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type in [
                UserTypeChoices.ADMIN,
                UserTypeChoices.RECEPTIONIST,
            ]
        )

class IsAdminOrDoctorOrReceptionist(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.user_type in [
                UserTypeChoices.ADMIN,
                UserTypeChoices.RECEPTIONIST,
                UserTypeChoices.DOCTOR,
            ]
        )


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return (
                request.user
                and request.user.is_authenticated
                and request.user.user_type == UserTypeChoices.RECEPTIONIST
        )