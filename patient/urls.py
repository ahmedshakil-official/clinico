from django.urls import path
from .views import (
    PatientListCreateView,
    PatientRetrieveUpdateView,
)

urlpatterns = [
    # Patient
    path("patients/", PatientListCreateView.as_view(), name="patient-list-create"),
    path("patients/<uuid:alias>/", PatientRetrieveUpdateView.as_view(), name="patient-detail"),

]