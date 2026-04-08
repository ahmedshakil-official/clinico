import csv
import os
import random
from datetime import date, time

from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker

from account.models import User
from appointment.models import Appointment, AppointmentStatusChoices
from common.enums import NameTitleChoices, UserTypeChoices
from doctor.models import Doctor
from core.models import PatientMedicalRecord
from patient.models import Patient


fake = Faker("en_AU")


class Command(BaseCommand):
    help = "Seed doctors, patients, appointments, and medical records from CSV"

    def add_arguments(self, parser):
        parser.add_argument("--csv_path", type=str, required=False)

    # ---------- HELPERS ----------

    def generate_unique_email(self, first_name, last_name):
        base = f"{first_name.lower()}.{last_name.lower()}@example.com"
        email = base
        counter = 1
        while User.objects.filter(email=email).exists():
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@example.com"
            counter += 1
        return email

    def random_phone(self):
        return "04" + "".join(random.choices("0123456789", k=8))

    def normalize_gender(self, value):
        value = str(value).strip().upper()
        if value == "MALE":
            return "MALE"
        if value == "FEMALE":
            return "FEMALE"
        return "OTHER"

    def estimate_dob(self, age):
        year = date.today().year - int(age)
        return date(year, 1, 1)

    # ---------- CREATE DATA ----------

    def create_doctors(self, count):
        doctors = []
        specializations = [
            "Cardiology", "Neurology", "Orthopedics",
            "Dermatology", "Pediatrics", "General Medicine"
        ]

        for _ in range(count):
            gender = random.choice(["MALE", "FEMALE"])
            first = fake.first_name_male() if gender == "MALE" else fake.first_name_female()
            last = fake.last_name()
            email = self.generate_unique_email(first, last)

            user = User.objects.create_user(
                email=email,
                password="Test@123456",
                first_name=first,
                last_name=last,
                phone=self.random_phone(),
                title=NameTitleChoices.DR,
                suburb=fake.city(),
                postal_code=fake.postcode(),
                address=fake.address(),
                user_type=UserTypeChoices.DOCTOR,
                is_active=True,
            )

            doctor = Doctor.objects.create(
                user=user,
                degree="MBBS",
                specialization=random.choice(specializations),
                joined_date=fake.date_between(start_date="-10y", end_date="today"),
                consultation_fee=random.randint(100, 500),
                chamber_room=f"Room-{random.randint(100,999)}",
                experience_years=random.randint(1, 20),
                bio=fake.text(max_nb_chars=80),
                gender=gender,
            )
            doctors.append(doctor)

        return doctors

    def create_patients(self, count):
        patients = []

        for _ in range(count):
            gender = random.choice(["MALE", "FEMALE"])
            first = fake.first_name_male() if gender == "MALE" else fake.first_name_female()
            last = fake.last_name()
            email = self.generate_unique_email(first, last)

            user = User(
                email=email,
                first_name=first,
                last_name=last,
                phone=self.random_phone(),
                title=NameTitleChoices.MR if gender == "MALE" else NameTitleChoices.MS,
                suburb=fake.city(),
                postal_code=fake.postcode(),
                address=fake.address(),
                user_type=UserTypeChoices.PATIENT,
                is_active=True,
            )
            user.set_unusable_password()
            user.save()

            age = random.randint(18, 80)

            patient = Patient.objects.create(
                user=user,
                date_of_birth=self.estimate_dob(age),
                gender=gender,
                emergency_contact_name=fake.name(),
                emergency_contact_phone=self.random_phone(),
                medical_history=fake.sentence(),
            )
            patients.append(patient)

        return patients

    def create_appointments(self, count, patients, doctors):
        appointments = []

        for _ in range(count):
            patient = random.choice(patients)
            doctor = random.choice(doctors)

            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_date=fake.date_between(start_date="-6M", end_date="+1M"),
                appointment_time=time(
                    hour=random.randint(9, 17),
                    minute=random.choice([0, 30])
                ),
                status=random.choice([
                    AppointmentStatusChoices.PENDING,
                    AppointmentStatusChoices.CONFIRMED,
                    AppointmentStatusChoices.COMPLETED,
                ]),
                reason=fake.sentence(),
                notes=fake.sentence(),
            )
            appointments.append(appointment)

        return appointments

    def create_records_from_csv(self, csv_path, appointments):
        count = 0

        random.shuffle(appointments)

        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            for i, row in enumerate(reader):
                if i >= len(appointments):
                    break

                appointment = appointments[i]
                patient = appointment.patient

                age = int(row["Age"])
                gender = self.normalize_gender(row["Gender"])

                # update patient from dataset
                patient.gender = gender
                patient.date_of_birth = self.estimate_dob(age)
                patient.save(update_fields=["gender", "date_of_birth", "updated_at"])

                PatientMedicalRecord.objects.create(
                    patient=patient,
                    appointment=appointment,
                    patient_record_id=int(row["Patient_ID"]),
                    age=age,
                    gender=row["Gender"],
                    condition=row["Condition"],
                    procedure=row["Procedure"],
                    cost=row["Cost"],
                    length_of_stay=int(row["Length_of_Stay"]),
                    readmission=row["Readmission"],
                    outcome=row["Outcome"],
                    satisfaction=int(row["Satisfaction"]),
                )

                count += 1

        return count

    # ---------- MAIN ----------

    @transaction.atomic
    def handle(self, *args, **options):

        csv_path = options.get("csv_path")

        if not csv_path:
            base_dir = os.path.dirname(__file__)
            csv_path = os.path.join(base_dir, "hospital_data.csv")

        self.stdout.write(self.style.WARNING("Creating doctors..."))
        doctors = self.create_doctors(100)

        self.stdout.write(self.style.WARNING("Creating patients..."))
        patients = self.create_patients(1000)

        self.stdout.write(self.style.WARNING("Creating appointments..."))
        appointments = self.create_appointments(1000, patients, doctors)

        self.stdout.write(self.style.WARNING("Importing CSV data..."))
        records = self.create_records_from_csv(csv_path, appointments)

        self.stdout.write(self.style.SUCCESS(f"Doctors: {len(doctors)}"))
        self.stdout.write(self.style.SUCCESS(f"Patients: {len(patients)}"))
        self.stdout.write(self.style.SUCCESS(f"Appointments: {len(appointments)}"))
        self.stdout.write(self.style.SUCCESS(f"Medical Records: {records}"))
        self.stdout.write(self.style.SUCCESS("Done!"))