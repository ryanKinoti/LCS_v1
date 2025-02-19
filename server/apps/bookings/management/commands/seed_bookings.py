# apps/bookings/management/commands/seed_bookings.py
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
import random

from django.utils import timezone
from datetime import datetime, timedelta

from apps.accounts.models import CustomerProfile, StaffProfile
from apps.inventory.models import Device, DevicePart
from apps.services.models import DetailedService
from apps.bookings.models import Booking, BookingParts
from utils.constants import BookingStatus, PaymentStatus, BUSINESS_HOURS

faker = Faker()


class Command(BaseCommand):
    help = 'Seed the database with realistic booking data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--bookings',
            default=20,
            type=int,
            help='Number of bookings to create'
        )

    def generate_business_datetime(self, start_date=None):
        """Generate a timezone-aware datetime during business hours"""
        if not start_date:
            # Generate a date within the last 30 days
            start_date = timezone.now() - timedelta(days=random.randint(0, 30))

        # Ensure start_date is timezone-aware
        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)

        # Parse business hours
        start_time = datetime.strptime(BUSINESS_HOURS['start_time'], '%I:%M %p').time()
        end_time = datetime.strptime(BUSINESS_HOURS['end_time'], '%I:%M %p').time()

        # Generate random time between business hours
        random_hour = random.randint(start_time.hour, end_time.hour - 1)
        random_minute = random.randint(0, 59)

        # Create the datetime in the current timezone
        naive_datetime = start_date.replace(
            hour=random_hour,
            minute=random_minute,
            second=0,
            microsecond=0
        )

        # Make it timezone-aware if it isn't already
        if timezone.is_naive(naive_datetime):
            return timezone.make_aware(naive_datetime)
        return naive_datetime

    def generate_diagnosis(self, service, status):
        """Generate realistic diagnosis based on service and status"""
        if status == BookingStatus.PENDING:
            return "Awaiting initial diagnosis"

        diagnoses = {
            'Screen Replacement': [
                "Screen shows flickering and dead pixels. Replacement needed.",
                "Cracked screen with touch functionality issues. Full replacement recommended.",
                "Display showing vertical lines. LCD replacement required."
            ],
            'Battery Replacement': [
                "Battery only holds charge for 30 minutes. Replacement needed.",
                "Battery swollen and affecting trackpad. Immediate replacement required.",
                "Battery not charging at all. Replacement recommended."
            ],
            'Operating System Installation': [
                "Current OS corrupted. Clean installation needed.",
                "System slow and unstable. Fresh OS installation recommended.",
                "Multiple boot failures. OS reinstallation required."
            ],
            'Virus Removal': [
                "Multiple malware detected. System requires cleaning.",
                "Ransomware detected. System cleanup needed.",
                "Browser hijackers found. Malware removal required."
            ],
            'Data Recovery': [
                "Hard drive making clicking sounds. Data recovery attempted.",
                "Corrupted file system. Professional recovery needed.",
                "Accidental format. Recovery of critical files required."
            ]
        }

        service_name = service.service.name
        if service_name in diagnoses:
            return random.choice(diagnoses[service_name])
        return f"Standard diagnosis for {service_name}"

    def handle(self, *args, **options):
        self.stdout.write("Creating bookings...")

        try:
            with transaction.atomic():
                # Get existing data
                customers = CustomerProfile.objects.all()
                technicians = StaffProfile.objects.filter(role='technician')
                detailed_services = DetailedService.objects.all()
                devices = Device.objects.all()
                parts = DevicePart.objects.filter(customer_laptop__isnull=True, status='in_stock')

                if not all([customers, technicians, detailed_services, devices, parts]):
                    self.stdout.write(self.style.ERROR(
                        "Missing required data. Please run seed_accounts, seed_services, "
                        "and seed_inventory first."
                    ))
                    return

                created_bookings = []
                past_date = timezone.now() - timedelta(days=30)
                future_date = timezone.now() + timedelta(days=30)

                for _ in range(options['bookings']):
                    # Select random related objects
                    customer = random.choice(customers)
                    technician = random.choice(technicians)
                    detailed_service = random.choice(detailed_services)

                    # Find or create a device for the customer
                    customer_devices = devices.filter(customer=customer.user)
                    device = random.choice(customer_devices) if customer_devices.exists() else None

                    # Generate booking datetime
                    if random.random() < 0.7:  # 70% past bookings, 30% future
                        booking_date = self.generate_business_datetime(
                            faker.date_time_between(start_date=past_date, end_date=timezone.now())
                        )
                        status = random.choice([
                            BookingStatus.COMPLETED,
                            BookingStatus.CANCELLED,
                            BookingStatus.IN_PROGRESS
                        ])
                        payment_status = random.choice([
                            PaymentStatus.PAID,
                            PaymentStatus.FAILED,
                            PaymentStatus.REFUNDED
                        ])
                    else:
                        booking_date = self.generate_business_datetime(
                            faker.date_time_between(start_date=timezone.now(), end_date=future_date)
                        )
                        status = random.choice([
                            BookingStatus.PENDING,
                            BookingStatus.CONFIRMED
                        ])
                        payment_status = PaymentStatus.PENDING

                    # Create booking
                    booking = Booking.objects.create(
                        customer=customer,
                        technician=technician,
                        detailed_service=detailed_service,
                        status=status,
                        scheduled_time=booking_date,
                        device=device,
                        payment_status=payment_status,
                        diagnosis=self.generate_diagnosis(detailed_service, status),
                        notes=faker.text(max_nb_chars=200) if random.random() < 0.5 else ""
                    )

                    # Add parts to completed or in-progress bookings
                    if status in [BookingStatus.COMPLETED, BookingStatus.IN_PROGRESS]:
                        # Add 1-3 parts to the booking
                        num_parts = random.randint(1, 3)
                        selected_parts = random.sample(list(parts), min(num_parts, len(parts)))
                        total_parts_cost = 0

                        for part in selected_parts:
                            quantity = random.randint(1, min(3, part.quantity))
                            BookingParts.objects.create(
                                booking=booking,
                                part=part,
                                quantity=quantity
                            )
                            total_parts_cost += part.price * quantity

                        booking.total_parts_cost = total_parts_cost
                        booking.save()

                    created_bookings.append(booking)

                # Calculate some statistics
                completed_bookings = sum(1 for b in created_bookings if b.status == BookingStatus.COMPLETED)
                pending_bookings = sum(1 for b in created_bookings if b.status == BookingStatus.PENDING)
                cancelled_bookings = sum(1 for b in created_bookings if b.status == BookingStatus.CANCELLED)

                self.stdout.write(self.style.SUCCESS(f"""
Successfully created {len(created_bookings)} bookings:
- {completed_bookings} completed bookings
- {pending_bookings} pending bookings
- {cancelled_bookings} cancelled bookings
"""))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding bookings: {str(e)}"))
