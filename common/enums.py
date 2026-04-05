from django.db import models
from django.utils.translation import gettext_lazy as _

class NameTitleChoices(models.TextChoices):
    MR = "MR", _("Mr.")
    MRS = "MRS", _("Mrs.")
    MS = "MS", _("Ms.")
    DR = "DR", _("Dr.")
    MISS = "MISS", _("Miss.")
    MADAM = "MADAM", _("Madam.")
    MAIDEN = "MAIDEN", _("Maiden.")
    PROFESSOR = "PROFESSOR", _("Professor.")
    DOCTOR = "DOCTOR", _("Doctor.")


class UserTypeChoices(models.TextChoices):
    ADMIN = "ADMIN", _("Admin")
    PATIENT = "PATIENT", _("Patient")
    DOCTOR = "DOCTOR", _("Doctor")
    RECEPTIONIST = "RECEPTIONIST", _("Receptionist")
    SELECT_USER_TYPE = "SELECT_USER_TYPE", _("Select User Type")