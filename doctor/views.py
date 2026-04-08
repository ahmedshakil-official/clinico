from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin, IsAdminOrReceptionist, IsAdminOrDoctorOrReceptionist
from doctor.models import Doctor
from doctor.serializers import (
    DoctorListCreateSerializer,
    DoctorRetrieveUpdateSerializer,
)


class DoctorListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DoctorListCreateSerializer
    filterset_fields = ["gender", "specialization", "joined_date"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone",
        "degree",
        "specialization",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "joined_date",
        "consultation_fee",
        "experience_years",
        "user__first_name",
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [IsAuthenticated, IsAdmin]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Doctor.objects.filter(
            is_removed=False,
            user__is_active=True,
        ).select_related("user")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class DoctorRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorRetrieveUpdateSerializer
    lookup_field = "alias"

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]
        else:
            permission_classes = [IsAuthenticated, IsAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return Doctor.objects.filter(
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