from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import CreatedAtUpdatedAtBaseModel
from common.enums import UserTypeChoices

User = settings.AUTH_USER_MODEL


class Receptionist(CreatedAtUpdatedAtBaseModel):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="receptionist_profile",
        verbose_name=_("User"),
    )

    slug = models.SlugField(max_length=255, unique=True, blank=True)

    employee_id = models.CharField(max_length=100, null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    shift = models.CharField(max_length=50, null=True, blank=True)  # Morning / Evening
    desk_number = models.CharField(max_length=50, null=True, blank=True)
    experience_years = models.PositiveIntegerField(null=True, blank=True)

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Receptionist"
        verbose_name_plural = "Receptionists"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(
                f"{self.user.first_name}-{self.user.last_name}-{str(self.alias)[:8]}"
            )
        super().save(*args, **kwargs)