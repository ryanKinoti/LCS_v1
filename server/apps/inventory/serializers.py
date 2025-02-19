# apps/inventory/serializers.py
from rest_framework import serializers
from apps.accounts.serializers import CustomerProfileSerializer, StaffProfileSerializer
from apps.bookings.serializers import BookingMinimalSerializer
from .models import Device, DevicePart, PartMovement, DeviceRepairHistory


class DevicePartMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal serializer for DevicePart model, used for nested relationships
    and list views where full details aren't necessary.
    """

    class Meta:
        model = DevicePart
        fields = ['id', 'name', 'model', 'serial_number', 'status', 'quantity']


class DeviceMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal serializer for Device model, used for nested relationships
    and list views where full details aren't necessary.
    """

    class Meta:
        model = Device
        fields = ['id', 'device_type', 'brand', 'model', 'serial_number', 'repair_status']


class DeviceCreateSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for creating new devices. Includes validation
    for required fields and proper customer assignment.
    """

    class Meta:
        model = Device
        fields = [
            'customer', 'device_type', 'brand', 'model',
            'serial_number', 'repair_status', 'sale_status'
        ]

    def validate_serial_number(self, value):
        """Ensure serial number is unique and properly formatted."""
        if Device.objects.filter(serial_number=value).exists():
            raise serializers.ValidationError("A device with this serial number already exists.")
        return value


class DeviceDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive device serializer for detailed views. Includes related
    parts and customer information.
    """
    customer = CustomerProfileSerializer(read_only=True)
    parts = DevicePartMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Device
        fields = [
            'id', 'customer', 'device_type', 'brand', 'model',
            'serial_number', 'repair_status', 'sale_status',
            'parts', 'created_at'
        ]


class DevicePartCreateSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for creating new device parts. Handles both
    standalone parts and parts associated with devices.
    """

    class Meta:
        model = DevicePart
        fields = [
            'customer_laptop', 'name', 'model', 'serial_number',
            'price', 'quantity', 'status', 'warranty_months',
            'minimum_stock'
        ]

    def validate(self, data):
        """
        Custom validation to ensure proper part creation based on
        whether it's standalone or associated with a device.
        """
        if data.get('customer_laptop') and data.get('quantity', 0) > 1:
            raise serializers.ValidationError(
                "Parts associated with a specific device cannot have quantity greater than 1"
            )

        if not data.get('customer_laptop') and data.get('quantity', 0) < data.get('minimum_stock', 1):
            raise serializers.ValidationError(
                "Standalone parts must have quantity greater than or equal to minimum stock"
            )

        return data


class DevicePartDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive part serializer for detailed views. Includes the associated
    device information if applicable.
    """
    customer_laptop = DeviceMinimalSerializer(read_only=True)

    class Meta:
        model = DevicePart
        fields = [
            'id', 'customer_laptop', 'name', 'model', 'serial_number',
            'price', 'quantity', 'status', 'warranty_months',
            'minimum_stock', 'created_at'
        ]


class PartMovementCreateSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for recording part movements. Includes
    validation for quantity changes.
    """

    class Meta:
        model = PartMovement
        fields = ['part', 'quantity', 'movement_type', 'notes']

    def validate(self, data):
        """Ensure valid quantity for movement type."""
        part = data['part']
        quantity = data['quantity']

        if data['movement_type'] in ['repair', 'sale']:
            if quantity > part.quantity:
                raise serializers.ValidationError(
                    f"Cannot move {quantity} units. Only {part.quantity} available."
                )

        return data

    def create(self, validated_data):
        """Create movement record and update part quantity."""
        part = validated_data['part']
        quantity = validated_data['quantity']

        # Update part quantity based on movement type
        if validated_data['movement_type'] in ['repair', 'sale']:
            part.quantity -= quantity
            if part.quantity == 0:
                part.status = 'out_of_stock'
            part.save()

        return super().create(validated_data)


class DeviceRepairHistoryCreateSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for creating repair history records.
    """

    class Meta:
        model = DeviceRepairHistory
        fields = ['device', 'booking', 'diagnosis', 'parts_replaced', 'technician']

    def validate(self, data):
        """Ensure device and parts compatibility."""
        device = data['device']
        parts = data.get('parts_replaced', [])

        # Verify device repair status
        if device.repair_status not in ['in_progress', None]:
            raise serializers.ValidationError(
                f"Cannot create repair history for device with status: {device.repair_status}"
            )

        return data


class DeviceRepairHistoryDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive repair history serializer for detailed views.
    Includes related device, booking, parts, and technician information.
    """
    device = DeviceMinimalSerializer(read_only=True)
    booking = BookingMinimalSerializer(read_only=True)
    parts_replaced = DevicePartMinimalSerializer(many=True, read_only=True)
    technician = StaffProfileSerializer(read_only=True)

    class Meta:
        model = DeviceRepairHistory
        fields = [
            'id', 'device', 'booking', 'diagnosis',
            'parts_replaced', 'repair_date', 'technician'
        ]
