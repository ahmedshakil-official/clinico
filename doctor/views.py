from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin
from doctor.models import Doctor
from doctor.serializers import (
    DoctorListCreateSerializer,
    DoctorRetrieveUpdateSerializer,
)


class DoctorListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DoctorListCreateSerializer

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
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = DoctorRetrieveUpdateSerializer
    lookup_field = "alias"

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