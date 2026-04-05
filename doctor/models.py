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


class Doctor(CreatedAtUpdatedAtBaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        verbose_name=_("User"),
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    degree = models.CharField(max_length=255, null=True, blank=True)
    specialization = models.CharField(max_length=255, null=True, blank=True)
    joined_date = models.DateField(null=True, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    chamber_room = models.CharField(max_length=100, null=True, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GenderChoices.choices,
        null=True,
        blank=True,
    )

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.user.first_name}-{self.user.last_name}-{str(self.alias)[:8]}"
            )
        super().save(*args, **kwargs)

