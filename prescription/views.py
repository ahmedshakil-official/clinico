from io import BytesIO
from django.http import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.db.models import Count
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.enums import UserTypeChoices
from common.permissions import IsAdminOrDoctorOrReceptionist, IsDoctor
from doctor.models import Doctor
from prescription.models import Prescription
from prescription.serializers import (
    PrescriptionListCreateSerializer,
    PrescriptionRetrieveUpdateSerializer,
)


class PrescriptionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PrescriptionListCreateSerializer

    filterset_fields = [
        "appointment",
    ]
    search_fields = [
        "prescription_number",
        "diagnosis",
        "medicines",
        "advice",
        "notes",
        "appointment__patient__user__first_name",
        "appointment__patient__user__last_name",
        "appointment__patient__user__email",
        "appointment__doctor__user__first_name",
        "appointment__doctor__user__last_name",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "appointment__appointment_date",
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [IsAuthenticated, IsDoctor]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = Prescription.objects.filter(
            is_removed=False,
            appointment__is_removed=False,
            appointment__patient__is_removed=False,
            appointment__patient__user__is_active=True,
            appointment__doctor__is_removed=False,
            appointment__doctor__user__is_active=True,
        ).select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__user",
            "appointment__doctor",
            "appointment__doctor__user",
            "created_by",
            "updated_by",
        )

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Prescription.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Prescription.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        doctor_profile = Doctor.objects.filter(
            user=user,
            is_removed=False,
            user__is_active=True,
        ).first()

        appointment = serializer.validated_data["appointment"]

        if not doctor_profile or appointment.doctor_id != doctor_profile.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only create prescriptions for your own appointments.")

        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class PrescriptionRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PrescriptionRetrieveUpdateSerializer
    lookup_field = "alias"

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]
        else:
            permission_classes = [IsAuthenticated, IsDoctor]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = Prescription.objects.filter(
            is_removed=False,
            appointment__is_removed=False,
            appointment__patient__is_removed=False,
            appointment__patient__user__is_active=True,
            appointment__doctor__is_removed=False,
            appointment__doctor__user__is_active=True,
        ).select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__user",
            "appointment__doctor",
            "appointment__doctor__user",
            "created_by",
            "updated_by",
        )

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Prescription.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Prescription.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        doctor_profile = Doctor.objects.filter(
            user=user,
            is_removed=False,
            user__is_active=True,
        ).first()

        appointment = serializer.instance.appointment
        if not doctor_profile or appointment.doctor_id != doctor_profile.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update prescriptions for your own appointments.")

        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        user = self.request.user
        doctor_profile = Doctor.objects.filter(
            user=user,
            is_removed=False,
            user__is_active=True,
        ).first()

        if not doctor_profile or instance.appointment.doctor_id != doctor_profile.id:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete prescriptions for your own appointments.")

        instance.is_removed = True
        instance.updated_by = self.request.user
        instance.save(update_fields=["is_removed", "updated_by", "updated_at"])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class PrescriptionDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Prescription.objects.filter(
            is_removed=False,
            appointment__is_removed=False,
            appointment__patient__is_removed=False,
            appointment__patient__user__is_active=True,
            appointment__doctor__is_removed=False,
            appointment__doctor__user__is_active=True,
        )

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Prescription.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Prescription.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.user)

        data = {
            "total_prescriptions": queryset.count(),
            "total_doctors": queryset.values("appointment__doctor").distinct().count(),
            "total_patients": queryset.values("appointment__patient").distinct().count(),
            "total_appointments": queryset.values("appointment").distinct().count(),
        }
        return Response(data)


class PrescriptionDoctorAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Prescription.objects.filter(
            is_removed=False,
            appointment__doctor__isnull=False,
        )

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Prescription.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Prescription.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = (
            self.get_queryset(request.user)
            .values(
                "appointment__doctor__id",
                "appointment__doctor__alias",
                "appointment__doctor__user__first_name",
                "appointment__doctor__user__last_name",
                "appointment__doctor__specialization",
            )
            .annotate(
                total_prescriptions=Count("id"),
            )
            .order_by("-total_prescriptions")
        )
        return Response(queryset)


class PrescriptionMonthlyTrendAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Prescription.objects.filter(
            is_removed=False,
            appointment__appointment_date__isnull=False,
        )

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Prescription.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Prescription.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = (
            self.get_queryset(request.user)
            .annotate(
                year=ExtractYear("appointment__appointment_date"),
                month=ExtractMonth("appointment__appointment_date"),
            )
            .values("year", "month")
            .annotate(total_prescriptions=Count("id"))
            .order_by("year", "month")
        )
        return Response(queryset)


class PrescriptionPDFAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Prescription.objects.filter(
            is_removed=False,
            appointment__is_removed=False,
            appointment__patient__is_removed=False,
            appointment__patient__user__is_active=True,
            appointment__doctor__is_removed=False,
            appointment__doctor__user__is_active=True,
        ).select_related(
            "appointment",
            "appointment__patient",
            "appointment__patient__user",
            "appointment__doctor",
            "appointment__doctor__user",
        )

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Prescription.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Prescription.objects.none()

    def get(self, request, alias, *args, **kwargs):
        prescription = self.get_queryset(request.user).filter(alias=alias).first()

        if not prescription:
            from rest_framework.exceptions import NotFound
            raise NotFound("Prescription not found.")

        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        y = height - 50

        def line(text, gap=20):
            nonlocal y
            p.drawString(50, y, text)
            y -= gap

        patient = prescription.appointment.patient
        doctor = prescription.appointment.doctor

        p.setFont("Helvetica-Bold", 16)
        line("PRESCRIPTION", 30)

        p.setFont("Helvetica", 11)
        line(f"Prescription Number: {prescription.prescription_number}")
        line(f"Appointment Date: {prescription.appointment.appointment_date}")
        line(f"Appointment Time: {prescription.appointment.appointment_time}")
        line("")

        p.setFont("Helvetica-Bold", 12)
        line("Doctor Information", 22)
        p.setFont("Helvetica", 11)
        line(f"Name: Dr. {doctor.user.first_name} {doctor.user.last_name}")
        line(f"Email: {doctor.user.email}")
        line(f"Specialization: {doctor.specialization or ''}")
        line("")

        p.setFont("Helvetica-Bold", 12)
        line("Patient Information", 22)
        p.setFont("Helvetica", 11)
        line(f"Name: {patient.user.first_name} {patient.user.last_name}")
        line(f"Email: {patient.user.email}")
        line(f"Phone: {patient.user.phone or ''}")
        line("")

        p.setFont("Helvetica-Bold", 12)
        line("Diagnosis", 22)
        p.setFont("Helvetica", 11)
        line(prescription.diagnosis or "")
        line("")

        p.setFont("Helvetica-Bold", 12)
        line("Medicines", 22)
        p.setFont("Helvetica", 11)
        for item in (prescription.medicines or "").splitlines():
            line(item or " ")
        line("")

        p.setFont("Helvetica-Bold", 12)
        line("Advice", 22)
        p.setFont("Helvetica", 11)
        for item in (prescription.advice or "").splitlines():
            line(item or " ")
        line("")

        p.setFont("Helvetica-Bold", 12)
        line("Notes", 22)
        p.setFont("Helvetica", 11)
        for item in (prescription.notes or "").splitlines():
            line(item or " ")

        p.showPage()
        p.save()
        buffer.seek(0)

        filename = f"{prescription.prescription_number}.pdf"
        return FileResponse(buffer, as_attachment=False, filename=filename, content_type="application/pdf")