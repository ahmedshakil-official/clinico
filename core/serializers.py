from rest_framework import serializers

from appointment.models import Appointment
from core.models import PatientMedicalRecord
from patient.models import Patient


class PatientNestedSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "alias",
            "slug",
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "gender",
            "blood_group",
        ]


class AppointmentNestedSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(source="doctor.id", read_only=True)
    doctor_alias = serializers.UUIDField(source="doctor.alias", read_only=True)
    doctor_slug = serializers.CharField(source="doctor.slug", read_only=True)
    doctor_first_name = serializers.CharField(source="doctor.user.first_name", read_only=True)
    doctor_last_name = serializers.CharField(source="doctor.user.last_name", read_only=True)
    doctor_email = serializers.EmailField(source="doctor.user.email", read_only=True)
    doctor_specialization = serializers.CharField(source="doctor.specialization", read_only=True)

    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    patient_alias = serializers.UUIDField(source="patient.alias", read_only=True)
    patient_slug = serializers.CharField(source="patient.slug", read_only=True)
    patient_first_name = serializers.CharField(source="patient.user.first_name", read_only=True)
    patient_last_name = serializers.CharField(source="patient.user.last_name", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "alias",
            "slug",
            "appointment_date",
            "appointment_time",
            "status",
            "reason",
            "notes",
            "doctor_id",
            "doctor_alias",
            "doctor_slug",
            "doctor_first_name",
            "doctor_last_name",
            "doctor_email",
            "doctor_specialization",
            "patient_id",
            "patient_alias",
            "patient_slug",
            "patient_first_name",
            "patient_last_name",
        ]


class PatientMedicalRecordListCreateSerializer(serializers.ModelSerializer):
    patient_details = PatientNestedSerializer(source="patient", read_only=True)
    appointment_details = AppointmentNestedSerializer(source="appointment", read_only=True)

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
            "patient_details",
            "appointment_details",
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
        read_only_fields = [
            "id",
            "alias",
            "slug",
            "patient_details",
            "appointment_details",
            "created_at",
            "updated_at",
        ]

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
    patient_details = PatientNestedSerializer(source="patient", read_only=True)
    appointment_details = AppointmentNestedSerializer(source="appointment", read_only=True)

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
            "patient_details",
            "appointment_details",
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
        read_only_fields = [
            "id",
            "alias",
            "slug",
            "patient_details",
            "appointment_details",
            "created_at",
            "updated_at",
        ]

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