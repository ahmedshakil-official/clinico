from django.db.models.signals import post_save
from django.dispatch import receiver

from common.enums import UserTypeChoices
from receptionist.models import Receptionist


@receiver(post_save, sender=Receptionist)
def set_receptionist_user_type(sender, instance, created, **kwargs):
    user = instance.user
    if user.user_type != UserTypeChoices.RECEPTIONIST:
        user.user_type = UserTypeChoices.RECEPTIONIST
        user.save(update_fields=["user_type"])