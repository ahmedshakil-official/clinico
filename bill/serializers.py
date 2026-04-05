from rest_framework import serializers
from django.db import transaction
# from common.models import User, UserProfile, Patient, Doctor, Receptionist, Appointment, Prescription, Billing
#
#
#
# class BillingSerializer(serializers.ModelSerializer):
#     patient_name = serializers.CharField(source='appointment.patient.__str__', read_only=True)
#
#     class Meta:
#         model = Billing
#         fields = ['id', 'appointment', 'patient_name', 'billing_amount', 'is_paid']
#
#     def update(self, instance, validated_data):
#         instance.is_paid = validated_data.get('is_paid', instance.is_paid)
#         instance.billing_amount = validated_data.get('billing_amount', instance.billing_amount)
#         instance.save()
#         return instance