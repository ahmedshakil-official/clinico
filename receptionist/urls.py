from django.urls import path

from receptionist.views import (
    ReceptionistListCreateAPIView,
    ReceptionistRetrieveUpdateDeleteAPIView,
)

urlpatterns = [
    path(
        "",
        ReceptionistListCreateAPIView.as_view(),
        name="receptionist-list-create",
    ),
    path(
        "<uuid:alias>/",
        ReceptionistRetrieveUpdateDeleteAPIView.as_view(),
        name="receptionist-detail",
    ),
]