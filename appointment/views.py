from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from common.enums import UserTypeChoices
from appointment.models import Appointment

from common.permissions import IsDoctorOrReceptionist
from appointment.serializers import (
    AppointmentListCreateSerializer,
    AppointmentRetrieveUpdateSerializer,
)
from doctor.models import Doctor


class AppointmentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsDoctorOrReceptionist]
    serializer_class = AppointmentListCreateSerializer

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