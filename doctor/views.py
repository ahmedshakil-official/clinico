from rest_framework import generics
from django.contrib.auth import get_user_model
from common.enums import UserTypeChoices
from .serializers import DoctorSerializer

User = get_user_model()

class DoctorListCreateView(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    lookup_field = "alias"

    def get_queryset(self):
        return User.objects.filter(user_type=UserTypeChoices.DOCTOR)

class DoctorRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DoctorSerializer
    lookup_field = "alias"

    def get_queryset(self):
        return User.objects.filter(user_type=UserTypeChoices.DOCTOR)