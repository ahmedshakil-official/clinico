from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bill.filters import BillFilter
from bill.models import Bill
from bill.serializers import (
    BillListCreateSerializer,
    BillRetrieveUpdateSerializer,
)
from common.enums import UserTypeChoices
from common.permissions import (
    IsAdminOrDoctorOrReceptionist,
    IsReceptionist,
)
from doctor.models import Doctor


class BillListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = BillListCreateSerializer
    filterset_class = BillFilter

    search_fields = [
        "bill_number",
        "appointment__patient__user__first_name",
        "appointment__patient__user__last_name",
        "appointment__patient__user__email",
        "appointment__doctor__user__first_name",
        "appointment__doctor__user__last_name",
        "appointment__doctor__specialization",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "amount",
        "discount",
        "tax",
        "total_amount",
        "appointment__appointment_date",
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            permission_classes = [IsAuthenticated, IsReceptionist]
        else:
            permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = Bill.objects.filter(
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
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Bill.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class BillRetrieveUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BillRetrieveUpdateSerializer
    lookup_field = "alias"

    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            permission_classes = [IsAuthenticated, IsReceptionist]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        queryset = Bill.objects.filter(
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
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Bill.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_destroy(self, instance):
        instance.is_removed = True
        instance.updated_by = self.request.user
        instance.save(update_fields=["is_removed", "updated_by", "updated_at"])


class BillDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Bill.objects.filter(
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
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()

            if not doctor_profile:
                return Bill.objects.none()

            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request.user)

        data = {
            "total_bills": queryset.count(),
            "total_amount": queryset.aggregate(total=Sum("amount"))["total"] or 0,
            "total_discount": queryset.aggregate(total=Sum("discount"))["total"] or 0,
            "total_tax": queryset.aggregate(total=Sum("tax"))["total"] or 0,
            "total_final_amount": queryset.aggregate(total=Sum("total_amount"))["total"] or 0,
            "average_bill_amount": queryset.aggregate(avg=Avg("total_amount"))["avg"] or 0,
            "paid_bills": queryset.filter(payment_status="PAID").count(),
            "pending_bills": queryset.filter(payment_status="PENDING").count(),
            "partial_bills": queryset.filter(payment_status="PARTIAL").count(),
            "cancelled_bills": queryset.filter(payment_status="CANCELLED").count(),
        }
        return Response(data)


class BillPaymentStatusAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Bill.objects.filter(is_removed=False)

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()
            if not doctor_profile:
                return Bill.objects.none()
            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = (
            self.get_queryset(request.user)
            .values("payment_status")
            .annotate(
                total_bills=Count("id"),
                total_amount=Sum("total_amount"),
            )
            .order_by("payment_status")
        )
        return Response(queryset)


class BillPaymentMethodAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Bill.objects.filter(is_removed=False)

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()
            if not doctor_profile:
                return Bill.objects.none()
            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = (
            self.get_queryset(request.user)
            .values("payment_method")
            .annotate(
                total_bills=Count("id"),
                total_amount=Sum("total_amount"),
            )
            .order_by("payment_method")
        )
        return Response(queryset)


class BillDoctorAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Bill.objects.filter(is_removed=False)

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()
            if not doctor_profile:
                return Bill.objects.none()
            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get(self, request, *args, **kwargs):
        base_qs = self.get_queryset(request.user)

        queryset = (
            base_qs
            .exclude(appointment__doctor__isnull=True)
            .values(
                "appointment__doctor__id",
                "appointment__doctor__alias",
                "appointment__doctor__user__first_name",
                "appointment__doctor__user__last_name",
                "appointment__doctor__specialization",
            )
            .annotate(
                total_bills=Count("id"),
                sum_total_amount=Sum("total_amount"),
                average_amount=Avg("total_amount"),
            )
            .order_by("-total_bills")
        )
        return Response(queryset)


class BillMonthlyTrendAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDoctorOrReceptionist]

    def get_queryset(self, user):
        queryset = Bill.objects.filter(is_removed=False)

        if user.user_type == UserTypeChoices.ADMIN:
            return queryset

        if user.user_type == UserTypeChoices.RECEPTIONIST:
            return queryset.filter(created_by=user)

        if user.user_type == UserTypeChoices.DOCTOR:
            doctor_profile = Doctor.objects.filter(
                user=user,
                is_removed=False,
                user__is_active=True,
            ).first()
            if not doctor_profile:
                return Bill.objects.none()
            return queryset.filter(appointment__doctor=doctor_profile)

        return Bill.objects.none()

    def get(self, request, *args, **kwargs):
        base_qs = self.get_queryset(request.user)

        queryset = (
            base_qs
            .exclude(appointment__appointment_date__isnull=True)
            .annotate(
                year=ExtractYear("appointment__appointment_date"),
                month=ExtractMonth("appointment__appointment_date"),
            )
            .values("year", "month")
            .annotate(
                total_bills=Count("id"),
                sum_total_amount=Sum("total_amount"),
                sum_discount=Sum("discount"),
                sum_tax=Sum("tax"),
                avg_total_amount=Avg("total_amount"),
            )
            .order_by("year", "month")
        )
        return Response(queryset)