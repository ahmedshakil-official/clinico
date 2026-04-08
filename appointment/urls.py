from django.urls import path

from appointment.views import (
    AppointmentListCreateAPIView,
    AppointmentRetrieveUpdateDeleteAPIView, DoctorOwnAppointmentListAPIView,
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
    path(
        "my-appointments/",
        DoctorOwnAppointmentListAPIView.as_view(),
        name="doctor-own-appointments",
    ),
]