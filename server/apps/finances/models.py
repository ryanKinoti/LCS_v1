# apps/finances/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils.constants import Finances

class ActiveTransactionManager(models.Manager):
    """Manager that returns only active transactions by default"""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

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
    transaction_type = models.CharField(max_length=20,choices=Finances.TRANSACTION_TYPES,)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Total amount expected for this transaction")
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Current total of all payments made")
    )
    status = models.CharField(max_length=10, choices=Finances.CHOICES, default=Finances.PENDING)
    payment_method = models.CharField(max_length=20, choices=Finances.PAYMENT_METHODS)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True,
        help_text=_("Soft delete flag. Inactive transactions are hidden but preserved.")
    )
    deactivated_at = models.DateTimeField(null=True, blank=True)
    deactivated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='deactivated_transactions'
    )
    deactivation_reason = models.TextField(blank=True)

    objects = models.Manager()
    active_objects = ActiveTransactionManager()

    def clean(self):
        """Validate transaction amounts"""
        super().clean()
        if self.total_amount <= 0:
            raise ValidationError(_("Total amount must be greater than zero"))
        if self.amount_paid > self.total_amount:
            raise ValidationError(_("Amount paid cannot exceed total amount"))

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # Generate reference number based on transaction type and ID
            last_transaction = Transaction.objects.order_by('-id').first()
            next_id = (last_transaction.id + 1) if last_transaction else 1
            self.reference_number = f"TRX{next_id:06d}"

        super().save(*args, **kwargs)

    def soft_delete(self, user, reason=''):
        """Soft delete the transaction while maintaining audit trail"""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.deactivated_by = user
        self.deactivation_reason = reason
        self.save()

    @property
    def balance_due(self):
        """Calculate remaining balance to be paid"""
        return self.total_amount - self.amount_paid

    @property
    def payment_progress(self):
        """Calculate payment progress as a percentage"""
        if self.total_amount == 0:
            return 0
        return (self.amount_paid / self.total_amount) * 100

    def update_payment_status(self):
        """Update payment status based on amounts"""
        if self.amount_paid == 0:
            self.status = Finances.PENDING
        elif self.amount_paid < self.total_amount:
            self.status = Finances.PARTIAL
        elif self.amount_paid == self.total_amount:
            self.status = Finances.PAID
        self.save()

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
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text=_(
            "Unique receipt number for this payment made by corresponding payment method e.g.: MPESA transaction codes"
        )
    )
    recorded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    def clean(self):
        """Validate payment record"""
        super().clean()
        if self.amount_paid <= 0:
            raise ValidationError(_("Payment amount must be greater than zero"))

        # Check if this payment would exceed transaction total
        total_paid = self.transaction.amount_paid + self.amount_paid
        if total_paid > self.transaction.total_amount:
            raise ValidationError(_(
                f"This payment of {self.amount_paid} would exceed the total amount due."
                f"Remaining balance: {self.transaction.balance_due}"
            ))

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
