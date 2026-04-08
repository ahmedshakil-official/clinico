from django.db.models import Avg, Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdmin
from core.filters import PatientMedicalRecordFilter
from core.models import PatientMedicalRecord
from core.serializers import (
    PatientMedicalRecordListCreateSerializer,
    PatientMedicalRecordRetrieveUpdateSerializer,
)


class PatientMedicalRecordListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PatientMedicalRecordListCreateSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    filterset_class = PatientMedicalRecordFilter

    search_fields = [
        "condition",
        "procedure",
        "outcome",
        "readmission",
        "patient__user__first_name",
        "patient__user__last_name",
        "patient__user__email",
        "appointment__doctor__user__first_name",
        "appointment__doctor__user__last_name",
        "appointment__doctor__specialization",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "age",
        "cost",
        "length_of_stay",
        "satisfaction",
        "appointment__appointment_date",
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


class PatientMedicalRecordDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = PatientMedicalRecord.objects.filter(is_removed=False)

        data = {
            "total_records": queryset.count(),
            "total_cost": queryset.aggregate(total=Sum("cost"))["total"] or 0,
            "average_cost": queryset.aggregate(avg=Avg("cost"))["avg"] or 0,
            "average_age": queryset.aggregate(avg=Avg("age"))["avg"] or 0,
            "average_length_of_stay": queryset.aggregate(avg=Avg("length_of_stay"))["avg"] or 0,
            "average_satisfaction": queryset.aggregate(avg=Avg("satisfaction"))["avg"] or 0,
            "readmission_yes_count": queryset.filter(readmission__iexact="Yes").count(),
            "readmission_no_count": queryset.filter(readmission__iexact="No").count(),
        }
        return Response(data)


class PatientMedicalRecordConditionAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(is_removed=False)
            .values("condition")
            .annotate(
                total_records=Count("id"),
                total_cost=Sum("cost"),
                average_cost=Avg("cost"),
                average_stay=Avg("length_of_stay"),
                average_satisfaction=Avg("satisfaction"),
            )
            .order_by("-total_records")
        )
        return Response(queryset)


class PatientMedicalRecordProcedureAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(is_removed=False)
            .values("procedure")
            .annotate(
                total_records=Count("id"),
                total_cost=Sum("cost"),
                average_cost=Avg("cost"),
                average_stay=Avg("length_of_stay"),
                average_satisfaction=Avg("satisfaction"),
            )
            .order_by("-total_records")
        )
        return Response(queryset)


class PatientMedicalRecordOutcomeAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(is_removed=False)
            .values("outcome")
            .annotate(
                total_records=Count("id"),
                total_cost=Sum("cost"),
                average_cost=Avg("cost"),
                average_satisfaction=Avg("satisfaction"),
            )
            .order_by("-total_records")
        )
        return Response(queryset)


class PatientMedicalRecordDoctorAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(
                is_removed=False,
                appointment__doctor__isnull=False,
            )
            .values(
                "appointment__doctor__id",
                "appointment__doctor__alias",
                "appointment__doctor__user__first_name",
                "appointment__doctor__user__last_name",
                "appointment__doctor__specialization",
            )
            .annotate(
                total_records=Count("id"),
                total_cost=Sum("cost"),
                average_cost=Avg("cost"),
                average_satisfaction=Avg("satisfaction"),
            )
            .order_by("-total_records")
        )
        return Response(queryset)


class PatientMedicalRecordMonthlyCostTrendAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(
                is_removed=False,
                appointment__appointment_date__isnull=False,
            )
            .annotate(
                year=ExtractYear("appointment__appointment_date"),
                month=ExtractMonth("appointment__appointment_date"),
            )
            .values("year", "month")
            .annotate(
                total_cost=Sum("cost"),
                total_records=Count("id"),
                average_cost=Avg("cost"),
            )
            .order_by("year", "month")
        )
        return Response(queryset)


class PatientMedicalRecordMonthlyRecordTrendAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(
                is_removed=False,
                appointment__appointment_date__isnull=False,
            )
            .annotate(
                year=ExtractYear("appointment__appointment_date"),
                month=ExtractMonth("appointment__appointment_date"),
            )
            .values("year", "month")
            .annotate(total_records=Count("id"))
            .order_by("year", "month")
        )
        return Response(queryset)


class PatientMedicalRecordSatisfactionDistributionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(is_removed=False)
            .values("satisfaction")
            .annotate(total_records=Count("id"))
            .order_by("satisfaction")
        )
        return Response(queryset)


class PatientMedicalRecordReadmissionDistributionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(is_removed=False)
            .values("readmission")
            .annotate(total_records=Count("id"))
            .order_by("readmission")
        )
        return Response(queryset)


class PatientMedicalRecordGenderDistributionAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = (
            PatientMedicalRecord.objects.filter(is_removed=False)
            .values("gender")
            .annotate(total_records=Count("id"))
            .order_by("gender")
        )
        return Response(queryset)


class PatientMedicalRecordAgeGroupAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = PatientMedicalRecord.objects.filter(is_removed=False)

        age_groups = [
            {"label": "0-18", "min": 0, "max": 18},
            {"label": "19-30", "min": 19, "max": 30},
            {"label": "31-45", "min": 31, "max": 45},
            {"label": "46-60", "min": 46, "max": 60},
            {"label": "61+", "min": 61, "max": 200},
        ]

        data = []
        for group in age_groups:
            records = queryset.filter(age__gte=group["min"], age__lte=group["max"])
            data.append({
                "age_group": group["label"],
                "total_records": records.count(),
                "total_cost": records.aggregate(total=Sum("cost"))["total"] or 0,
                "average_cost": records.aggregate(avg=Avg("cost"))["avg"] or 0,
                "average_satisfaction": records.aggregate(avg=Avg("satisfaction"))["avg"] or 0,
            })

        return Response(data)


class PatientMedicalRecordLengthOfStayAnalyticsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, *args, **kwargs):
        queryset = PatientMedicalRecord.objects.filter(is_removed=False)

        stay_groups = [
            {"label": "1-3", "min": 1, "max": 3},
            {"label": "4-7", "min": 4, "max": 7},
            {"label": "8-14", "min": 8, "max": 14},
            {"label": "15+", "min": 15, "max": 1000},
        ]

        data = []
        for group in stay_groups:
            records = queryset.filter(
                length_of_stay__gte=group["min"],
                length_of_stay__lte=group["max"],
            )
            data.append({
                "length_of_stay_group": group["label"],
                "total_records": records.count(),
                "total_cost": records.aggregate(total=Sum("cost"))["total"] or 0,
                "average_cost": records.aggregate(avg=Avg("cost"))["avg"] or 0,
                "average_satisfaction": records.aggregate(avg=Avg("satisfaction"))["avg"] or 0,
            })

        return Response(data)