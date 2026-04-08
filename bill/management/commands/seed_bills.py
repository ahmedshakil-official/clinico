import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from appointment.models import Appointment
from bill.models import Bill, PaymentMethodChoices, PaymentStatusChoices
from common.enums import UserTypeChoices
from account.models import User


fake = Faker("en_AU")


class Command(BaseCommand):
    help = "Create 500 fake bills using existing appointments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=500,
            help="Number of bills to create",
        )

    def get_receptionists(self):
        return list(
            User.objects.filter(
                is_active=True,
                user_type=UserTypeChoices.RECEPTIONIST,
            )
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

    def generate_bill_data(self):
        amount = Decimal(str(round(random.uniform(100, 5000), 2)))
        discount = Decimal(str(round(random.uniform(0, 500), 2)))
        tax = Decimal(str(round(random.uniform(0, 300), 2)))

        payment_status = random.choice(
            [
                PaymentStatusChoices.PENDING,
                PaymentStatusChoices.PAID,
                PaymentStatusChoices.PARTIAL,
                PaymentStatusChoices.CANCELLED,
            ]
        )

        payment_method = random.choice(
            [
                PaymentMethodChoices.CASH,
                PaymentMethodChoices.CARD,
                PaymentMethodChoices.ONLINE,
                PaymentMethodChoices.BANK,
            ]
        )

        notes = fake.sentence(nb_words=8)

        return {
            "amount": amount,
            "discount": discount,
            "tax": tax,
            "payment_status": payment_status,
            "payment_method": payment_method,
            "notes": notes,
        }

    @transaction.atomic
    def handle(self, *args, **options):
        count = options["count"]

        appointments = self.get_appointments()
        receptionists = self.get_receptionists()

        if not appointments:
            self.stdout.write(
                self.style.ERROR("No valid appointments found.")
            )
            return

        if not receptionists:
            self.stdout.write(
                self.style.ERROR("No active receptionist users found.")
            )
            return

        created_count = 0

        for _ in range(count):
            appointment = random.choice(appointments)
            receptionist = random.choice(receptionists)
            bill_data = self.generate_bill_data()

            Bill.objects.create(
                appointment=appointment,
                amount=bill_data["amount"],
                discount=bill_data["discount"],
                tax=bill_data["tax"],
                payment_status=bill_data["payment_status"],
                payment_method=bill_data["payment_method"],
                notes=bill_data["notes"],
                created_by=receptionist,
                updated_by=receptionist,
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created {created_count} bills.")
        )