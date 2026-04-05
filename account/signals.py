# from django.db.models.signals import post_save
# from django.dispatch import receiver
#
# from common.models import User


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     """
#     Automatically creates a UserProfile when a new User is saved.
#     """
#     if created:
#         # We default to PATIENT, but this can be overridden during registration logic
#         UserProfile.objects.get_or_create(user=instance, defaults={'role': 'PATIENT'})
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     """
#     Ensures the profile is saved whenever the User object is saved.
#     """
#     if hasattr(instance, 'profile'):
#         instance.profile.save()