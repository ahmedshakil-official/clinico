from django.db.models.signals import post_save
from django.dispatch import receiver

from common.enums import UserTypeChoices
from doctor.models import Doctor


@receiver(post_save, sender=Doctor)
def set_doctor_user_type(sender, instance, created, **kwargs):
    user = instance.user
    if user.user_type != UserTypeChoices.DOCTOR:
        user.user_type = UserTypeChoices.DOCTOR
        user.save(update_fields=["user_type"])