from django.utils.text import slugify
from django.db import models
from django.utils.translation import gettext_lazy as _

from appointment.models import Appointment
from common.models import CreatedAtUpdatedAtBaseModel
from patient.models import Patient


class PatientMedicalRecord(CreatedAtUpdatedAtBaseModel):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records",
        verbose_name=_("Patient"),
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medical_records",
        verbose_name=_("Appointment"),
    )

    slug = models.SlugField(max_length=255, unique=True, blank=True)

    patient_record_id = models.PositiveIntegerField(
        db_index=True,
        null=True,
        blank=True,
        help_text=_("Patient_ID from spreadsheet"),
    )

    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20)
    condition = models.CharField(max_length=255)
    procedure = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    length_of_stay = models.PositiveIntegerField()
    readmission = models.CharField(max_length=20)
    outcome = models.CharField(max_length=100)
    satisfaction = models.PositiveIntegerField()

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        if self.patient:
            return f"{self.patient.user.first_name} - {self.condition}"
        return f"Record {self.patient_record_id} - {self.condition}"

    def save(self, *args, **kwargs):
        if not self.slug:
            patient_part = (
                f"{self.patient.user.first_name}-{self.patient.user.last_name}"
                if self.patient else f"patient-{self.patient_record_id}"
            )

            appointment_part = (
                str(self.appointment.alias)[:8] if self.appointment else "no-appointment"
            )

            self.slug = slugify(
                f"{patient_part}-{self.condition}-{appointment_part}-{str(self.alias)[:8]}"
            )

        super().save(*args, **kwargs)