# apps/bookings/models.py
from datetime import datetime, timedelta

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import CustomerProfile, StaffProfile
from apps.finances.models import Transaction
from apps.inventory.models import DevicePart
from apps.services.models import Service, DetailedService
from utils.constants import BookingStatus, Finances, BUSINESS_HOURS


class Booking(models.Model):
    """
    Represents a customer booking for a specific repair or service appointment.
    Tracks essential details such as the customer, assigned technician, associated service(s), scheduled time, device being worked on, and financials (e.g., parts cost, payment status).
    Also includes validation to ensure scheduling respects business hours, technician availability, and overlaps with other bookings.
    """
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='bookings')
    technician = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_bookings')
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.PROTECT)
    status = models.CharField(max_length=100, choices=BookingStatus.CHOICES, default=BookingStatus.PENDING)
    scheduled_time = models.DateTimeField()
    device = models.ForeignKey('inventory.Device', on_delete=models.SET_NULL, null=True)
    parts_used = models.ManyToManyField('inventory.DevicePart', through='BookingParts')
    is_active = models.BooleanField(default=True)

    # financials
    total_parts_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=Finances.CHOICES, default=Finances.PENDING)
    transactions = GenericRelation(Transaction)

    # additional info
    notes = models.TextField(blank=True, help_text=_("Additional details about the appointment."))
    diagnosis = models.TextField(blank=True, help_text=_("Technician's diagnosis of the issue"))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def job_card_number(self):
        """Format the auto-generated ID as a job card number"""
        return str(self.id).zfill(4)

    def __str__(self):
        return f'Booking {self.id} | {self.customer.user.get_full_name()} -> {self.status}'

    def clean(self):
        if not self.scheduled_time:
            return

        # Convert to local time for validation
        local_time = timezone.localtime(self.scheduled_time)

        # 1. Check business hours
        business_start = datetime.strptime(BUSINESS_HOURS['start_time'], '%I:%M %p').hour
        business_end = datetime.strptime(BUSINESS_HOURS['end_time'], '%I:%M %p').hour

        if not (business_start <= local_time.hour < business_end):
            raise ValidationError(_('Scheduled time must be during business hours: '
                                    f'{BUSINESS_HOURS["start_time"]} - {BUSINESS_HOURS["end_time"]}'))

        if not self.technician:
            return

        # 2. Check technician availability
        day_of_week = local_time.strftime('%A').lower()
        technician_schedule = self.technician.availability.get(day_of_week, {})

        if not technician_schedule:
            raise ValidationError(_(f'Technician is not available on {day_of_week}'))

        tech_start = technician_schedule.get('start')
        tech_end = technician_schedule.get('end')

        if not tech_start or not tech_end:  # Missing or invalid schedule data
            raise ValidationError(_('Technician\'s schedule is incomplete for the day'))

        # Validate time format before parsing
        try:
            tech_start_hour = datetime.strptime(tech_start, '%H:%M').hour
            tech_end_hour = datetime.strptime(tech_end, '%H:%M').hour
        except (TypeError, ValueError):
            raise ValidationError(_('Invalid time format in technician\'s schedule (expected: HH:MM)'))

        if not (tech_start_hour <= local_time.hour < tech_end_hour):
            raise ValidationError(_('Scheduled time is outside technician\'s working hours'))

        # 3. Check for overlapping bookings
        service_duration = self.detailed_service.service.estimated_time.total_seconds() if self.detailed_service.service else 60  # Default 1 hour if no service specified
        booking_end_time = self.scheduled_time + timedelta(minutes=service_duration)

        overlapping_bookings = Booking.objects.filter(
            technician=self.technician,
            status__in=[BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS],
            scheduled_time__lt=booking_end_time,
            scheduled_time__gt=self.scheduled_time - timedelta(minutes=service_duration)
        ).exclude(pk=self.pk)

        if overlapping_bookings.exists():
            raise ValidationError(_('This time slot overlaps with another booking'))


class BookingParts(models.Model):
    """
    Tracks the parts used in a specific booking for repair or service.
    Links the `Booking` with the `DevicePart` and records details like the quantity of parts used.
    Includes validation to ensure sufficient stock availability for shop-owned parts and ensures customer-specific parts match the correct booking device.
    """
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT)
    part = models.ForeignKey(DevicePart, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        # Rule 1: Validate against stock levels for shop-owned parts
        if self.part.customer_laptop is None:  # Shop-owned part
            if self.quantity > self.part.quantity:
                raise ValidationError(
                    f"Not enough stock for {self.part.name}. "
                    f"Available: {self.part.quantity}, Requested: {self.quantity}."
                )
        else:  # Rule 2: Validate use of customer-specific part
            if self.part.customer_laptop != self.booking.device:
                raise ValidationError(
                    f"Part {self.part.name} is tied to a different customer device and cannot be used for this booking."
                )

    def save(self, *args, **kwargs):
        # Perform validations
        self.clean()
        super().save(*args, **kwargs)
