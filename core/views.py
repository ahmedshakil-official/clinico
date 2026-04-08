from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.permissions import IsAdmin
from core.models import PatientMedicalRecord
from core.serializers import (
    PatientMedicalRecordListCreateSerializer,
    PatientMedicalRecordRetrieveUpdateSerializer,
)


class PatientMedicalRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PatientMedicalRecordListCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    filterset_fields = [
        "gender",
        "condition",
        "procedure",
        "readmission",
        "outcome",
        "patient_record_id",
        "patient",
        "appointment",
    ]
    search_fields = [
        "condition",
        "procedure",
        "outcome",
        "patient__user__first_name",
        "patient__user__last_name",
        "patient__user__email",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "age",
        "cost",
        "length_of_stay",
        "satisfaction",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return PatientMedicalRecord.objects.filter(
            is_removed=False
        ).select_related(
            "patient",
            "patient__user",
            "appointment",
            "appointment__patient",
            "appointment__patient__user",
            "appointment__doctor",
            "appointment__doctor__user",
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class PatientMedicalRecordRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientMedicalRecordRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = "alias"

    def get_queryset(self):
        return PatientMedicalRecord.objects.filter(
            is_removed=False
        ).select_related(
            "patient",
            "patient__user",
            "appointment",
            "appointment__patient",
            "appointment__patient__user",
            "appointment__doctor",
            "appointment__doctor__user",
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_destroy(self, instance):
        instance.is_removed = True
        instance.updated_by = self.request.user
        instance.save(update_fields=["is_removed", "updated_by", "updated_at"])