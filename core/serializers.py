from rest_framework import serializers

from appointment.models import Appointment
from core.models import PatientMedicalRecord
from patient.models import Patient


class PatientMedicalRecordListCreateSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.filter(is_removed=False, user__is_active=True),
        required=False,
        allow_null=True,
    )
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(is_removed=False),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = PatientMedicalRecord
        fields = [
            "id",
            "alias",
            "slug",
            "patient",
            "appointment",
            "patient_record_id",
            "age",
            "gender",
            "condition",
            "procedure",
            "cost",
            "length_of_stay",
            "readmission",
            "outcome",
            "satisfaction",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def validate(self, attrs):
        patient = attrs.get("patient")
        appointment = attrs.get("appointment")

        if not patient and not appointment:
            raise serializers.ValidationError(
                "Either patient or appointment must be provided."
            )

        if appointment and not patient:
            attrs["patient"] = appointment.patient

        if appointment and patient and appointment.patient_id != patient.id:
            raise serializers.ValidationError({
                "appointment": "Selected appointment does not belong to the selected patient."
            })

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        return PatientMedicalRecord.objects.create(
            created_by=request.user,
            updated_by=request.user,
            **validated_data,
        )


class PatientMedicalRecordRetrieveUpdateSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.filter(is_removed=False, user__is_active=True),
        required=False,
        allow_null=True,
    )
    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(is_removed=False),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = PatientMedicalRecord
        fields = [
            "id",
            "alias",
            "slug",
            "patient",
            "appointment",
            "patient_record_id",
            "age",
            "gender",
            "condition",
            "procedure",
            "cost",
            "length_of_stay",
            "readmission",
            "outcome",
            "satisfaction",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def validate(self, attrs):
        patient = attrs.get("patient", getattr(self.instance, "patient", None))
        appointment = attrs.get("appointment", getattr(self.instance, "appointment", None))

        if not patient and not appointment:
            raise serializers.ValidationError(
                "Either patient or appointment must be provided."
            )

        if appointment and not patient:
            attrs["patient"] = appointment.patient
            patient = appointment.patient

        if appointment and patient and appointment.patient_id != patient.id:
            raise serializers.ValidationError({
                "appointment": "Selected appointment does not belong to the selected patient."
            })

        return attrs

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            instance.updated_by = request.user

        instance.save()
        return instance