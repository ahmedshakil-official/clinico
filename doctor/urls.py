from django.urls import path

from doctor.views import (
    DoctorListCreateAPIView,
    DoctorRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path(
        "",
        DoctorListCreateAPIView.as_view(),
        name="doctor-list-create",
    ),
    path(
        "<uuid:alias>/",
        DoctorRetrieveUpdateDeleteAPIView.as_view(),
        name="doctor-detail",
    ),
]