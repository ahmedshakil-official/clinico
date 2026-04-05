from rest_framework import serializers

from appointment.models import Appointment
from patient.models import Patient
from doctor.models import Doctor
from common.serializers import PatientNestedSerializer, DoctorNestedSerializer


class CreatedByNestedSerializer(serializers.Serializer):
    alias = serializers.UUIDField(read_only=True)
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)
    user_type = serializers.CharField(read_only=True)

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class AppointmentListCreateSerializer(serializers.ModelSerializer):
    patient = PatientNestedSerializer(read_only=True)
    doctor = DoctorNestedSerializer(read_only=True)
    created_by_details = CreatedByNestedSerializer(source="created_by_user", read_only=True)

    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.filter(is_removed=False, user__is_active=True),
        source="patient",
        write_only=True,
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.filter(is_removed=False, user__is_active=True),
        source="doctor",
        write_only=True,
    )

    alias = serializers.UUIDField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "alias",
            "slug",
            "patient",
            "doctor",
            "patient_id",
            "doctor_id",
            "created_by_details",
            "appointment_date",
            "appointment_time",
            "status",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        return Appointment.objects.create(
            created_by_user=request.user,
            created_by=request.user,
            updated_by=request.user,
            **validated_data,
        )


class AppointmentRetrieveUpdateSerializer(serializers.ModelSerializer):
    patient = PatientNestedSerializer(read_only=True)
    doctor = DoctorNestedSerializer(read_only=True)
    created_by_details = CreatedByNestedSerializer(source="created_by_user", read_only=True)

    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.filter(is_removed=False, user__is_active=True),
        source="patient",
        write_only=True,
        required=False,
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.filter(is_removed=False, user__is_active=True),
        source="doctor",
        write_only=True,
        required=False,
    )

    alias = serializers.UUIDField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "alias",
            "slug",
            "patient",
            "doctor",
            "patient_id",
            "doctor_id",
            "created_by_details",
            "appointment_date",
            "appointment_time",
            "status",
            "reason",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "alias", "slug", "created_at", "updated_at"]

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            instance.updated_by = request.user

        instance.save()
        return instance