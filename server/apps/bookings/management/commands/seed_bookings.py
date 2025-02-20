# apps/bookings/management/commands/seed_bookings.py
import random
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction as t
from django.utils import timezone
from faker import Faker

from apps.accounts.models import CustomerProfile, StaffProfile
from apps.bookings.models import Booking, BookingParts
from apps.finances.models import Transaction, PaymentRecord
from apps.inventory.models import Device, DevicePart
from apps.services.models import DetailedService
from utils.constants import BookingStatus, Finances, BUSINESS_HOURS

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
            start_date = timezone.now() - timedelta(days=random.randint(0, 30))

        if timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)

        start_time = datetime.strptime(BUSINESS_HOURS['start_time'], '%I:%M %p').time()
        end_time = datetime.strptime(BUSINESS_HOURS['end_time'], '%I:%M %p').time()

        random_hour = random.randint(start_time.hour, end_time.hour - 1)
        random_minute = random.randint(0, 59)

        naive_datetime = start_date.replace(
            hour=random_hour,
            minute=random_minute,
            second=0,
            microsecond=0
        )

        return timezone.make_aware(naive_datetime) if timezone.is_naive(naive_datetime) else naive_datetime

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
        return random.choice(diagnoses.get(service_name, [f"Standard diagnosis for {service_name}"]))

    def create_transaction(self, booking, amount, status):
        """Create a transaction and payment record for a booking"""
        content_type = ContentType.objects.get_for_model(Booking)

        # Generate unique reference number
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        random_suffix = faker.random_number(digits=4)
        reference_number = f"LCS_TRX{timestamp}{random_suffix}"

        payment_method = random.choice([choice[0] for choice in Finances.PAYMENT_METHODS])

        amount = Decimal(str(amount))

        transaction = Transaction.objects.create(
            reference_number=reference_number,
            content_type=content_type,
            object_id=booking.id,
            transaction_type=Finances.BOOKING_PAYMENT,
            total_amount=amount,
            status=status,
            payment_method=payment_method,
            created_by=booking.customer.user,
            notes=faker.text(max_nb_chars=100)
        )

        # Create payment records for paid or partially paid transactions
        if status in [Finances.PAID, Finances.PARTIAL]:
            amount_to_pay = amount if status == Finances.PAID else amount * Decimal('0.5')
            PaymentRecord.objects.create(
                transaction=transaction,
                amount_paid=amount_to_pay,
                payment_method=payment_method,
                receipt_number=f"LCS_RCPT{faker.random_number(digits=8)}",
                recorded_by=booking.customer.user,
                notes=faker.text(max_nb_chars=100)
            )
            transaction.amount_paid = amount_to_pay
            transaction.save()

        return transaction

    def handle(self, *args, **options):
        self.stdout.write("Creating bookings...")

        try:
            with t.atomic():
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

                    # Determine booking datetime and status
                    if random.random() < 0.7:  # 70% past bookings
                        booking_date = self.generate_business_datetime(
                            faker.date_time_between(start_date=past_date, end_date=timezone.now())
                        )
                        status = random.choice([
                            BookingStatus.COMPLETED,
                            BookingStatus.CANCELLED,
                            BookingStatus.IN_PROGRESS
                        ])
                        payment_status = random.choice([
                            Finances.PAID,
                            Finances.FAILED,
                            Finances.PARTIAL
                        ])
                    else:  # 30% future bookings
                        booking_date = self.generate_business_datetime(
                            faker.date_time_between(start_date=timezone.now(), end_date=future_date)
                        )
                        status = random.choice([
                            BookingStatus.PENDING,
                            BookingStatus.CONFIRMED
                        ])
                        payment_status = Finances.PENDING

                    # Create booking
                    booking = Booking.objects.create(
                        customer=customer,
                        technician=technician,
                        detailed_service=detailed_service,
                        status=status,
                        scheduled_time=booking_date,
                        device=device,
                        diagnosis=self.generate_diagnosis(detailed_service, status),
                        notes=faker.text(max_nb_chars=200) if random.random() < 0.5 else ""
                    )

                    # Add parts to completed or in-progress bookings
                    total_parts_cost = 0
                    if status in [BookingStatus.COMPLETED, BookingStatus.IN_PROGRESS]:
                        num_parts = random.randint(1, 3)
                        selected_parts = random.sample(list(parts), min(num_parts, len(parts)))

                        for part in selected_parts:
                            quantity = random.randint(1, min(3, part.quantity))
                            BookingParts.objects.create(
                                booking=booking,
                                part=part,
                                quantity=quantity
                            )
                            total_parts_cost += part.price * quantity

                    # Calculate total amount and create transaction
                    total_amount = detailed_service.price + total_parts_cost
                    transaction = self.create_transaction(booking, total_amount, payment_status)

                    created_bookings.append(booking)

                # Print statistics
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
