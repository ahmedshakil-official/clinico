from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin
from receptionist.models import Receptionist
from receptionist.serializers import (
    ReceptionistListCreateSerializer,
    ReceptionistRetrieveUpdateSerializer,
)


class ReceptionistListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ReceptionistListCreateSerializer
    filterset_fields = ["joining_date", "shift", "experience_years"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone",
        "employee_id",
        "desk_number",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "joining_date",
        "experience_years",
        "user__first_name",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Receptionist.objects.filter(
            is_removed=False,
            user__is_active=True,
        ).select_related("user")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ReceptionistRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ReceptionistRetrieveUpdateSerializer
    lookup_field = "alias"

    def get_queryset(self):
        return Receptionist.objects.filter(
            is_removed=False,
            user__is_active=True,
        ).select_related("user")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_destroy(self, instance):
        instance.is_removed = True
        instance.updated_by = self.request.user
        instance.save(update_fields=["is_removed", "updated_by", "updated_at"])

        user = instance.user
        user.is_active = False
        user.save(update_fields=["is_active"])