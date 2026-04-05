from rest_framework import generics
from django.contrib.auth import get_user_model
from common.enums import UserTypeChoices
from .serializers import PatientSerializer

User = get_user_model()


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    lookup_field = "alias"

    def get_queryset(self):
        return User.objects.filter(user_type=UserTypeChoices.PATIENT)


class PatientRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = PatientSerializer
    lookup_field = "alias"

    def get_queryset(self):
        return User.objects.filter(user_type=UserTypeChoices.PATIENT)