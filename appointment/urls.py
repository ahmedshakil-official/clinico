from django.urls import path

from appointment.views import (
    AppointmentListCreateAPIView,
    AppointmentRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path(
        "",
        AppointmentListCreateAPIView.as_view(),
        name="appointment-list-create",
    ),
    path(
        "<uuid:alias>/",
        AppointmentRetrieveUpdateDeleteAPIView.as_view(),
        name="appointment-detail",
    ),
]