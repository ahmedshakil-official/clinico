# from rest_framework import generics
# from rest_framework.exceptions import PermissionDenied
#
# from common.models import Prescription
# from prescription.serializers import PrescriptionSerializer
#
#
# class PrescriptionCreateView(generics.CreateAPIView):
#     queryset = Prescription.objects.all()
#     serializer_class = PrescriptionSerializer
#
#     def perform_create(self, serializer):
#         if self.request.user.profile.role != 'DOCTOR':
#             raise PermissionDenied("Only Doctors can issue prescriptions.")
#         serializer.save()