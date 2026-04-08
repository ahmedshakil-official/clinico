from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import CreatedAtUpdatedAtBaseModel
from patient.models import Patient
from doctor.models import Doctor
from django.conf import settings

User = settings.AUTH_USER_MODEL


class AppointmentStatusChoices(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    CONFIRMED = "CONFIRMED", _("Confirmed")
    COMPLETED = "COMPLETED", _("Completed")
    CANCELLED = "CANCELLED", _("Cancelled")


class Appointment(CreatedAtUpdatedAtBaseModel):
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name=_("Patient"),
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name=_("Doctor"),
    )

    created_by_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_appointments",
        verbose_name=_("Created By User"),
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatusChoices.choices,
        default=AppointmentStatusChoices.PENDING,
    )
    reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient.user.first_name} with Dr. {self.doctor.user.first_name} on {self.appointment_date}"

    def save(self, *args, **kwargs):
        if not self.slug:
            patient_name = f"{self.patient.user.first_name}-{self.patient.user.last_name}"
            doctor_name = f"{self.doctor.user.first_name}-{self.doctor.user.last_name}"
            self.slug = slugify(
                f"{patient_name}-{doctor_name}-{self.appointment_date}-{str(self.alias)[:8]}"
            )
        super().save(*args, **kwargs)

