from django.urls import path

from prescription.views import (
    PrescriptionListCreateAPIView,
    PrescriptionRetrieveUpdateDeleteAPIView,
    PrescriptionDashboardAPIView,
    PrescriptionDoctorAnalyticsAPIView,
    PrescriptionMonthlyTrendAnalyticsAPIView,
    PrescriptionPDFAPIView,
)

urlpatterns = [
    # =========================
    # CRUD
    # =========================
    path(
        "",
        PrescriptionListCreateAPIView.as_view(),
        name="prescription-list-create",
    ),
    path(
        "<uuid:alias>/",
        PrescriptionRetrieveUpdateDeleteAPIView.as_view(),
        name="prescription-detail",
    ),

    # =========================
    # PDF
    # =========================
    path(
        "<uuid:alias>/pdf/",
        PrescriptionPDFAPIView.as_view(),
        name="prescription-pdf",
    ),

    # =========================
    # Dashboard & Analytics
    # =========================
    path(
        "dashboard/",
        PrescriptionDashboardAPIView.as_view(),
        name="prescription-dashboard",
    ),
    path(
        "analytics/doctor/",
        PrescriptionDoctorAnalyticsAPIView.as_view(),
        name="prescription-doctor-analytics",
    ),
    path(
        "analytics/monthly-trend/",
        PrescriptionMonthlyTrendAnalyticsAPIView.as_view(),
        name="prescription-monthly-trend-analytics",
    ),
]