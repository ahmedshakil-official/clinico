from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import CreatedAtUpdatedAtBaseModel
from common.enums import UserTypeChoices

User = settings.AUTH_USER_MODEL


class GenderChoices(models.TextChoices):
    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")
    OTHER = "OTHER", _("Other")


class BloodGroupChoices(models.TextChoices):
    A_POSITIVE = "A+", _("A+")
    A_NEGATIVE = "A-", _("A-")
    B_POSITIVE = "B+", _("B+")
    B_NEGATIVE = "B-", _("B-")
    AB_POSITIVE = "AB+", _("AB+")
    AB_NEGATIVE = "AB-", _("AB-")
    O_POSITIVE = "O+", _("O+")
    O_NEGATIVE = "O-", _("O-")


class Patient(CreatedAtUpdatedAtBaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        verbose_name=_("User"),
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    receptionist = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="receptionist_created_patients",
        verbose_name=_("Receptionist"),
        limit_choices_to={"user_type": UserTypeChoices.RECEPTIONIST},
    )

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GenderChoices.choices,
        null=True,
        blank=True,
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BloodGroupChoices.choices,
        null=True,
        blank=True,
    )
    emergency_contact_name = models.CharField(max_length=150, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=24, null=True, blank=True)
    medical_history = models.TextField(null=True, blank=True)

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(
                f"{self.user.first_name}-{self.user.last_name}-{str(self.alias)[:8]}"
            )
            self.slug = base_slug
        super().save(*args, **kwargs)