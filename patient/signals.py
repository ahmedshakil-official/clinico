from django.db.models.signals import post_save
from django.dispatch import receiver

from common.enums import UserTypeChoices
from patient.models import Patient


@receiver(post_save, sender=Patient)
def set_patient_user_type(sender, instance, created, **kwargs):
    user = instance.user
    if user.user_type != UserTypeChoices.PATIENT:
        user.user_type = UserTypeChoices.PATIENT
        user.save(update_fields=["user_type"])