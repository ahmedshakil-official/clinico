from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.enums import UserTypeChoices
from appointment.models import Appointment

from common.permissions import IsDoctorOrReceptionist, IsDoctor
from appointment.serializers import (
    AppointmentListCreateSerializer,
    AppointmentRetrieveUpdateSerializer,
)
from doctor.models import Doctor


class AppointmentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsDoctorOrReceptionist]
    serializer_class = AppointmentListCreateSerializer
    filterset_fields = ["status", "appointment_date", "doctor", "patient"]
    search_fields = [
        "patient__user__first_name",
        "patient__user__last_name",
        "patient__user__email",
        "doctor__user__first_name",
        "doctor__user__last_name",
        "doctor__specialization",
        "reason",
        "notes",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "appointment_date",
        "appointment_time",
        "status",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        queryset = Appointment.objects.filter(
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

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Appointment.objects.none()

            return queryset.filter(
                Q(doctor=doctor_profile) | Q(created_by_user=user)
            ).distinct()

        return Appointment.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class AppointmentRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AppointmentRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrReceptionist]
    lookup_field = "alias"

    def get_queryset(self):
        user = self.request.user

        queryset = Appointment.objects.filter(
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

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Appointment.objects.none()

            return queryset.filter(
                Q(doctor=doctor_profile) | Q(created_by_user=user)
            ).distinct()

        return Appointment.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_destroy(self, instance):
        instance.is_removed = True
        instance.updated_by = self.request.user
        instance.save(update_fields=["is_removed", "updated_by", "updated_at"])


class DoctorOwnAppointmentListAPIView(generics.ListAPIView):
    serializer_class = AppointmentListCreateSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    filterset_fields = ["status", "appointment_date"]
    search_fields = [
        "patient__user__first_name",
        "patient__user__last_name",
        "patient__user__email",
        "reason",
        "notes",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "appointment_date",
        "appointment_time",
    ]
    ordering = ["-created_at"]   # recent created first

    def get_queryset(self):
        doctor_profile = Doctor.objects.filter(
            user=self.request.user,
            is_removed=False,
            user__is_active=True,
        ).first()

        if not doctor_profile:
            return Appointment.objects.none()

        return Appointment.objects.filter(
            is_removed=False,
            doctor=doctor_profile,
            patient__is_removed=False,
            patient__user__is_active=True,
        ).select_related(
            "patient",
            "patient__user",
            "doctor",
            "doctor__user",
            "created_by_user",
        ).order_by("-created_at")