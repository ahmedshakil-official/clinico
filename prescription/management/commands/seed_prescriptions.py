import random

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from prescription.models import Prescription
from appointment.models import Appointment


fake = Faker("en_AU")


class Command(BaseCommand):
    help = "Create fake prescriptions using existing appointments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=500,
            help="Number of prescriptions to create",
        )

    def get_appointments(self):
        return list(
            Appointment.objects.filter(
                is_removed=False,
                patient__is_removed=False,
                patient__user__is_active=True,
                doctor__is_removed=False,
                doctor__user__is_active=True,
            ).select_related(
                "patient",
                "patient__user",
                "doctor",
                "doctor__user",
            )
        )

    def generate_diagnosis(self):
        choices = [
            "Seasonal flu",
            "Viral fever",
            "Hypertension",
            "Diabetes mellitus",
            "Migraine",
            "Skin allergy",
            "Gastric ulcer",
            "Back pain",
            "Respiratory infection",
            "General weakness",
        ]
        return random.choice(choices)

    def generate_medicines(self):
        lines = [
            "Paracetamol 500mg - 1 tablet twice daily for 5 days",
            "Omeprazole 20mg - 1 capsule before breakfast for 7 days",
            "Vitamin C - 1 tablet daily for 10 days",
            "Antihistamine - 1 tablet at night for 5 days",
            "ORS - as needed",
        ]
        count = random.randint(2, 4)
        return "\n".join(random.sample(lines, count))

    def generate_advice(self):
        choices = [
            "Take rest and drink plenty of water.",
            "Avoid oily and spicy foods.",
            "Come for follow-up after 7 days.",
            "Maintain regular exercise and diet control.",
            "Monitor blood pressure daily.",
            "Take medicines after meals.",
        ]
        count = random.randint(1, 3)
        return "\n".join(random.sample(choices, count))

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]
        appointments = self.get_appointments()

        if not appointments:
            self.stdout.write(self.style.ERROR("No valid appointments found."))
            return

        created_count = 0

        for _ in range(count):
            appointment = random.choice(appointments)

            Prescription.objects.create(
                appointment=appointment,
                diagnosis=self.generate_diagnosis(),
                medicines=self.generate_medicines(),
                advice=self.generate_advice(),
                notes=fake.sentence(nb_words=10),
                created_by=appointment.doctor.user if appointment.doctor and appointment.doctor.user else None,
                updated_by=appointment.doctor.user if appointment.doctor and appointment.doctor.user else None,
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} prescriptions.")
        )