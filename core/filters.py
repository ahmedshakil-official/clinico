import django_filters

from core.models import PatientMedicalRecord


class PatientMedicalRecordFilter(django_filters.FilterSet):
    created_at_after = django_filters.DateFilter(field_name="created_at", lookup_expr="date__gte")
    created_at_before = django_filters.DateFilter(field_name="created_at", lookup_expr="date__lte")

    cost_min = django_filters.NumberFilter(field_name="cost", lookup_expr="gte")
    cost_max = django_filters.NumberFilter(field_name="cost", lookup_expr="lte")

    age_min = django_filters.NumberFilter(field_name="age", lookup_expr="gte")
    age_max = django_filters.NumberFilter(field_name="age", lookup_expr="lte")

    stay_min = django_filters.NumberFilter(field_name="length_of_stay", lookup_expr="gte")
    stay_max = django_filters.NumberFilter(field_name="length_of_stay", lookup_expr="lte")

    satisfaction_min = django_filters.NumberFilter(field_name="satisfaction", lookup_expr="gte")
    satisfaction_max = django_filters.NumberFilter(field_name="satisfaction", lookup_expr="lte")

    appointment_date_after = django_filters.DateFilter(field_name="appointment__appointment_date", lookup_expr="gte")
    appointment_date_before = django_filters.DateFilter(field_name="appointment__appointment_date", lookup_expr="lte")

    class Meta:
        model = PatientMedicalRecord
        fields = [
            "gender",
            "condition",
            "procedure",
            "readmission",
            "outcome",
            "patient_record_id",
            "patient",
            "appointment",
        ]