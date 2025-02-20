# apps/finances/management/commands/seed_finances.py
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from apps.bookings.models import Booking
from apps.finances.models import Transaction, FinancialSummary

faker = Faker()


class Command(BaseCommand):
    help = 'Seed the database with financial records'

    def create_financial_summary(self, date):
        """Create or update financial summary for a date"""
        daily_transactions = Transaction.objects.filter(
            created_at__date=date,
            is_active=True
        )

        summary, created = FinancialSummary.objects.get_or_create(date=date)

        # Calculate totals
        payment_transactions = daily_transactions.filter(transaction_type='booking_payment')
        expense_transactions = daily_transactions.filter(transaction_type='expense')

        summary.total_revenue = sum(t.amount_paid for t in payment_transactions)
        summary.total_expenses = sum(t.amount_paid for t in expense_transactions)

        # Calculate service and parts revenue from bookings
        booking_type = ContentType.objects.get_for_model(Booking)
        booking_transactions = payment_transactions.filter(content_type=booking_type)

        summary.service_revenue = sum(
            t.content_object.detailed_service.price
            for t in booking_transactions
            if t.content_object and t.content_object.detailed_service
        )

        summary.parts_revenue = sum(
            t.content_object.total_parts_cost
            for t in booking_transactions
            if t.content_object
        )

        summary.outstanding_payments = sum(t.balance_due for t in daily_transactions)
        summary.save()

        return summary

    def handle(self, *args, **options):
        self.stdout.write("Creating financial summaries...")

        try:
            with transaction.atomic():
                # Create financial summaries for the past 30 days
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=30)
                current_date = start_date

                summaries_created = 0
                while current_date <= end_date:
                    self.create_financial_summary(current_date)
                    summaries_created += 1
                    current_date += timedelta(days=1)

                self.stdout.write(self.style.SUCCESS(
                    f"Successfully created {summaries_created} financial summaries"
                ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding finances: {str(e)}"))
