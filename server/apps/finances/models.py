# apps/finances/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from utils.constants import Finances


class Transaction(models.Model):
    """
    Central model for tracking all financial transactions in the system.
    Uses GenericForeignKey to link to any model that generates financial activity (bookings, inventory purchases, etc.).
    Maintains a complete audit trail of all money movements within the system.
    """
    reference_number = models.CharField(
        max_length=20,
        unique=True,
        help_text=_("Unique reference number for this transaction")
    )

    # Generic relation to allow linking to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    transaction_type = models.CharField(
        max_length=20,
        choices=Finances.TRANSACTION_TYPES,
        help_text=_("Type of financial transaction")
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Transaction amount in KES")
    )

    status = models.CharField(
        max_length=10,
        choices=Finances.CHOICES,
        default=Finances.PENDING
    )

    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', _('Cash')),
            ('card', _('Card')),
            ('mpesa', _('M-Pesa')),
            ('bank_transfer', _('Bank Transfer')),
        ]
    )

    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_("Transaction amount must be greater than zero"))

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate reference number based on transaction type and ID
            last_transaction = Transaction.objects.order_by('-id').first()
            next_id = (last_transaction.id + 1) if last_transaction else 1
            self.reference_number = f"TRX{next_id:06d}"

        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']


class PaymentRecord(models.Model):
    """
    Tracks individual payments made against transactions.
    Useful for handling partial payments and maintaining payment history.
    """
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=Finances.PAYMENT_METHODS)
    receipt_number = models.CharField(max_length=50, unique=True)
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def clean(self):
        if self.amount_paid <= 0:
            raise ValidationError(_("Payment amount must be greater than zero"))

    class Meta:
        ordering = ['-payment_date']


class FinancialSummary(models.Model):
    """
    Maintains running totals and summaries of financial activity.
    Updated through signals to ensure real-time accuracy of financial data.
    """
    date = models.DateField(unique=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    service_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    parts_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    outstanding_payments = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Financial Summary"
        verbose_name_plural = "Financial Summaries"
        ordering = ['-date']
