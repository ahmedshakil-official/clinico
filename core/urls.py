from django.urls import path

from core.views import (
    PatientMedicalRecordListCreateAPIView,
    PatientMedicalRecordRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path(
        "",
        PatientMedicalRecordListCreateAPIView.as_view(),
        name="patient-medical-record-list-create",
    ),
    path(
        "<uuid:alias>/",
        PatientMedicalRecordRetrieveUpdateDeleteAPIView.as_view(),
        name="patient-medical-record-detail",
    ),
]