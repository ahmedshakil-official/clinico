from rest_framework import serializers

from appointment.models import Appointment
from prescription.models import Prescription


class PrescriptionAppointmentNestedSerializer(serializers.ModelSerializer):
    patient_first_name = serializers.CharField(source="patient.user.first_name", read_only=True)
    patient_last_name = serializers.CharField(source="patient.user.last_name", read_only=True)
    patient_email = serializers.EmailField(source="patient.user.email", read_only=True)

    doctor_first_name = serializers.CharField(source="doctor.user.first_name", read_only=True)
    doctor_last_name = serializers.CharField(source="doctor.user.last_name", read_only=True)
    doctor_email = serializers.EmailField(source="doctor.user.email", read_only=True)
    doctor_specialization = serializers.CharField(source="doctor.specialization", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "alias",
            "slug",
            "appointment_date",
            "appointment_time",
            "status",
            "patient_first_name",
            "patient_last_name",
            "patient_email",
            "doctor_first_name",
            "doctor_last_name",
            "doctor_email",
            "doctor_specialization",
        ]


class PrescriptionListCreateSerializer(serializers.ModelSerializer):
    appointment_details = PrescriptionAppointmentNestedSerializer(source="appointment", read_only=True)

    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(is_removed=False),
    )

    class Meta:
        model = Prescription
        fields = [
            "id",
            "alias",
            "slug",
            "prescription_number",
            "appointment",
            "appointment_details",
            "diagnosis",
            "medicines",
            "advice",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "alias",
            "slug",
            "prescription_number",
            "appointment_details",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        return Prescription.objects.create(
            created_by=request.user,
            updated_by=request.user,
            **validated_data,
        )


class PrescriptionRetrieveUpdateSerializer(serializers.ModelSerializer):
    appointment_details = PrescriptionAppointmentNestedSerializer(source="appointment", read_only=True)

    appointment = serializers.PrimaryKeyRelatedField(
        queryset=Appointment.objects.filter(is_removed=False),
        required=False,
    )

    class Meta:
        model = Prescription
        fields = [
            "id",
            "alias",
            "slug",
            "prescription_number",
            "appointment",
            "appointment_details",
            "diagnosis",
            "medicines",
            "advice",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "alias",
            "slug",
            "prescription_number",
            "appointment_details",
            "created_at",
            "updated_at",
        ]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            instance.updated_by = request.user

        instance.save()
        return instance