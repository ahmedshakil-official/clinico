from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from appointment.models import Appointment
from common.models import CreatedAtUpdatedAtBaseModel


class Prescription(CreatedAtUpdatedAtBaseModel):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        verbose_name=_("Appointment"),
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    prescription_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        blank=True,
    )
    diagnosis = models.TextField(null=True, blank=True)
    medicines = models.TextField(help_text=_("Write medicines and dosage instructions"))
    advice = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prescription"
        verbose_name_plural = "Prescriptions"

    def __str__(self):
        return f"{self.prescription_number} - {self.appointment.patient.user.first_name}"

    def save(self, *args, **kwargs):
        if not self.prescription_number:
            self.prescription_number = f"RX-{str(self.alias)[:8].upper()}"

        if not self.slug:
            self.slug = slugify(f"{self.prescription_number}-{str(self.alias)[:8]}")

        super().save(*args, **kwargs)