from django.urls import path

from common.views import (
    AppointmentAllListAPIView,
    DoctorAllListAPIView,
    PatientAllListAPIView,
)

urlpatterns = [
    path("appointment-list/", AppointmentAllListAPIView.as_view(), name="appointment-list"),
    path("doctor-list/", DoctorAllListAPIView.as_view(), name="doctor-list"),
    path("patient-list/", PatientAllListAPIView.as_view(), name="patient-list"),
]