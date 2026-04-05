from django.urls import path
from .views import (
    DoctorListCreateView,
    DoctorRetrieveUpdateView,
)

urlpatterns = [
    # Doctor
    path("doctors/", DoctorListCreateView.as_view(), name="doctor-list-create"),
    path("doctors/<uuid:alias>/", DoctorRetrieveUpdateView.as_view(), name="doctor-detail"),
]