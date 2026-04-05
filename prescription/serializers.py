# from rest_framework import serializers
# from django.db import transaction
# from common.models import User, UserProfile, Patient, Doctor, Receptionist, Appointment, Prescription, Billing
#
#
# class PrescriptionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Prescription
#         fields = ['id', 'appointment', 'medication', 'dosage', 'prescribed_on']
#         read_only_fields = ['prescribed_on']