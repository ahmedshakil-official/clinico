from django.urls import path

from bill.views import (
    BillDashboardAPIView,
    BillDoctorAnalyticsAPIView,
    BillListCreateAPIView,
    BillMonthlyTrendAnalyticsAPIView,
    BillPaymentMethodAnalyticsAPIView,
    BillPaymentStatusAnalyticsAPIView,
    BillRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path(
        "",
        BillListCreateAPIView.as_view(),
        name="bill-list-create",
    ),
    path(
        "<uuid:alias>/",
        BillRetrieveUpdateDeleteAPIView.as_view(),
        name="bill-detail",
    ),
    path(
        "dashboard/",
        BillDashboardAPIView.as_view(),
        name="bill-dashboard",
    ),
    path(
        "analytics/payment-status/",
        BillPaymentStatusAnalyticsAPIView.as_view(),
        name="bill-payment-status-analytics",
    ),
    path(
        "analytics/payment-method/",
        BillPaymentMethodAnalyticsAPIView.as_view(),
        name="bill-payment-method-analytics",
    ),
    path(
        "analytics/doctor/",
        BillDoctorAnalyticsAPIView.as_view(),
        name="bill-doctor-analytics",
    ),
    path(
        "analytics/monthly-trend/",
        BillMonthlyTrendAnalyticsAPIView.as_view(),
        name="bill-monthly-trend-analytics",
    ),
]