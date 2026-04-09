from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from patient.models import Patient
from patient.serializers import PatientListCreateSerializer
from doctor.models import Doctor
from doctor.serializers import DoctorListCreateSerializer
from appointment.models import Appointment
from appointment.serializers import AppointmentListCreateSerializer


class DoctorAllListAPIView(generics.ListAPIView):
    serializer_class = DoctorListCreateSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["gender", "specialization", "joined_date"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone",
        "degree",
        "specialization",
        "chamber_room",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "joined_date",
        "consultation_fee",
        "experience_years",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Doctor.objects.filter(
            is_removed=False,
            user__is_active=True,
        ).select_related("user")




class PatientAllListAPIView(generics.ListAPIView):
    serializer_class = PatientListCreateSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["gender", "blood_group", "date_of_birth"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone",
        "emergency_contact_name",
        "medical_history",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "date_of_birth",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Patient.objects.filter(
            is_removed=False,
            user__is_active=True,
        ).select_related("user", "created_by", "updated_by")




class AppointmentAllListAPIView(generics.ListAPIView):
    serializer_class = AppointmentListCreateSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["status", "appointment_date", "doctor", "patient"]
    search_fields = [
        "patient__user__first_name",
        "patient__user__last_name",
        "patient__user__email",
        "doctor__user__first_name",
        "doctor__user__last_name",
        "reason",
        "notes",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "appointment_date",
        "appointment_time",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Appointment.objects.filter(
            is_removed=False,
            patient__is_removed=False,
            patient__user__is_active=True,
            doctor__is_removed=False,
            doctor__user__is_active=True,
        ).select_related(
            "patient",
            "patient__user",
            "doctor",
            "doctor__user",
            "created_by_user",
        )