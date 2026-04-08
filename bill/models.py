from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from appointment.models import Appointment
from common.models import CreatedAtUpdatedAtBaseModel


class PaymentStatusChoices(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    PAID = "PAID", _("Paid")
    PARTIAL = "PARTIAL", _("Partial")
    CANCELLED = "CANCELLED", _("Cancelled")


class PaymentMethodChoices(models.TextChoices):
    CASH = "CASH", _("Cash")
    CARD = "CARD", _("Card")
    ONLINE = "ONLINE", _("Online")
    BANK = "BANK", _("Bank Transfer")


class Bill(CreatedAtUpdatedAtBaseModel):
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name="bills",
        verbose_name=_("Appointment"),
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    bill_number = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        blank=True,
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.PENDING,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.CASH,
    )
    notes = models.TextField(null=True, blank=True)

    is_removed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Bill"
        verbose_name_plural = "Bills"

    def __str__(self):
        return f"{self.bill_number} - {self.appointment.patient.user.first_name}"

    def save(self, *args, **kwargs):
        self.total_amount = (self.amount or 0) - (self.discount or 0) + (self.tax or 0)

        if not self.bill_number:
            self.bill_number = f"BILL-{str(self.alias)[:8].upper()}"

        if not self.slug:
            self.slug = slugify(f"{self.bill_number}-{str(self.alias)[:8]}")

        super().save(*args, **kwargs)