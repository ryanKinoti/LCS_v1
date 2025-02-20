from rest_framework import serializers

from apps.inventory.models import Device, DevicePart


class DeviceMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal serializer for Device model, used for nested relationships
    and list views where full details aren't necessary.
    """

    class Meta:
        model = Device
        fields = ['id', 'device_type', 'brand', 'model', 'serial_number', 'repair_status']


class DevicePartMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal serializer for DevicePart model, used for nested relationships
    and list views where full details aren't necessary.
    """

    class Meta:
        model = DevicePart
        fields = ['id', 'name', 'model', 'serial_number', 'status', 'quantity']
