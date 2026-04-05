from django.urls import path

from patient.views import (
    PatientListCreateAPIView,
    PatientRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path("", PatientListCreateAPIView.as_view(), name="patient-list-create"),
    path(
        "<uuid:alias>/",
        PatientRetrieveUpdateDeleteAPIView.as_view(),
        name="patient-detail",
    ),
]