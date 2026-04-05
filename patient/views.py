from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from patient.models import Patient
from common.permissions import IsDoctorOrReceptionist
from patient.serializers import (
    PatientListCreateSerializer,
    PatientRetrieveUpdateSerializer,
)


class PatientListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PatientListCreateSerializer
    permission_classes = [IsAuthenticated,IsDoctorOrReceptionist]

    def get_queryset(self):
        return Patient.objects.filter(
            is_removed=False,
            receptionist=self.request.user,
            user__is_active=True,
        ).select_related("user", "receptionist")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class PatientRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrReceptionist]
    lookup_field = "alias"

    def get_queryset(self):
        return Patient.objects.filter(
            is_removed=False,
            receptionist=self.request.user,
            user__is_active=True,
        ).select_related("user", "receptionist")

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