from datetime import timezone, datetime

from rest_framework import serializers

from apps.accounts.serializers import CustomerProfileMinimalSerializer, StaffProfileMinimalSerializer
from apps.bookings.models import Booking, BookingParts
from apps.inventory.serializers import DeviceMinimalSerializer, DevicePartMinimalSerializer
from apps.services.serializers import DetailedServiceMinimalSerializer
from utils.constants import Finances, BUSINESS_HOURS, BookingStatus


class BookingPartsSerializer(serializers.ModelSerializer):
    """
    Serializer for managing parts used in a booking.
    Handles validation of part quantities and customer-specific parts.
    """
    part_details = DevicePartMinimalSerializer(source='part', read_only=True)

    class Meta:
        model = BookingParts
        fields = ['id', 'part', 'part_details', 'quantity']
        read_only_fields = ['id']

    def validate(self, data):
        """
        Validate part availability and ownership.
        """
        part = data['part']
        quantity = data['quantity']
        booking = self.context['booking']

        # Validate shop-owned parts quantity
        if not part.customer_laptop and quantity > part.quantity:
            raise serializers.ValidationError(
                f"Insufficient stock for {part.name}. Available: {part.quantity}, Requested: {quantity}"
            )

        # Validate customer-specific parts
        if part.customer_laptop and part.customer_laptop != booking.device:
            raise serializers.ValidationError(
                "This part belongs to a different customer device"
            )

        return data

    def validate_device(self, value):
        """Ensure device belongs to customer"""
        if value and value.customer != self.context['request'].user:
            raise serializers.ValidationError(
                "Device does not belong to the customer"
            )
        return value

    # Add payment validation
    def validate_payment_status(self, value):
        if value == Finances.PAID and not self.instance:
            raise serializers.ValidationError(
                "New bookings cannot be marked as paid"
            )
        return value


class BookingCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating bookings.
    Includes comprehensive validation for scheduling and business rules.
    """
    parts_used = BookingPartsSerializer(source='bookingparts_set', many=True, required=False)

    class Meta:
        model = Booking
        fields = [
            'customer', 'technician', 'detailed_service', 'status',
            'scheduled_time', 'device', 'parts_used', 'notes',
            'diagnosis', 'payment_status', 'is_active'
        ]

    def validate_scheduled_time(self, value):
        """
        Validate booking time against business hours and technician availability.
        """
        if not value:
            return value

        local_time = timezone.localtime(value)

        # Check business hours
        business_start = datetime.strptime(BUSINESS_HOURS['start_time'], '%I:%M %p').hour
        business_end = datetime.strptime(BUSINESS_HOURS['end_time'], '%I:%M %p').hour

        if not (business_start <= local_time.hour < business_end):
            raise serializers.ValidationError(
                f"Scheduled time must be within business hours ({BUSINESS_HOURS['start_time']} - {BUSINESS_HOURS['end_time']})"
            )

        return value

    def validate(self, data):
        """
        Cross-field validation for booking creation/update.
        """
        # Validate technician availability
        if 'technician' in data and 'scheduled_time' in data:
            technician = data['technician']
            scheduled_time = data['scheduled_time']

            if technician and scheduled_time:
                day_of_week = scheduled_time.strftime('%A').lower()
                technician_schedule = technician.availability.get(day_of_week, {})

                if not technician_schedule:
                    raise serializers.ValidationError(
                        f"Selected technician is not available on {day_of_week}"
                    )

        # Validate booking status transitions
        if self.instance and 'status' in data:
            current_status = self.instance.status
            new_status = data['status']

            invalid_transitions = {
                BookingStatus.COMPLETED: [BookingStatus.PENDING, BookingStatus.CONFIRMED],
                BookingStatus.CANCELLED: [BookingStatus.COMPLETED]
            }

            if new_status in invalid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from {current_status} to {new_status}"
                )

        return data

    def create(self, validated_data):
        """
        Create booking with associated parts.
        """
        parts_data = validated_data.pop('bookingparts_set', [])
        booking = super().create(validated_data)

        # Create booking parts
        for part_data in parts_data:
            BookingParts.objects.create(booking=booking, **part_data)

        return booking

    def update(self, instance, validated_data):
        """
        Update booking and manage parts changes.
        """
        parts_data = validated_data.pop('bookingparts_set', None)
        booking = super().update(instance, validated_data)

        if parts_data is not None:
            # Clear existing parts if new parts data provided
            BookingParts.objects.filter(booking=booking).delete()

            # Create new booking parts
            for part_data in parts_data:
                BookingParts.objects.create(booking=booking, **part_data)

        return booking


class BookingDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for viewing complete booking information.
    Includes all related data needed for frontend display.
    """
    customer = CustomerProfileMinimalSerializer(read_only=True)
    technician = StaffProfileMinimalSerializer(read_only=True)
    detailed_service = DetailedServiceMinimalSerializer(read_only=True)
    device = DeviceMinimalSerializer(read_only=True)
    parts_used = BookingPartsSerializer(source='bookingparts_set', many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'job_card_number', 'customer', 'technician',
            'detailed_service', 'status', 'scheduled_time', 'device',
            'parts_used', 'total_parts_cost', 'payment_status',
            'notes', 'diagnosis', 'is_active', 'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 'job_card_number', 'total_parts_cost',
            'created_at', 'updated_at'
        ]
