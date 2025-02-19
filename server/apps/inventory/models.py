# apps/inventory/models.py
from django.db import models
from apps.accounts.models import User
from utils.constants import DeviceParts, Devices


class Device(models.Model):
    """
    Represents a device owned by a customer or the shop itself, such as a laptop, smartphone, or tablet.
    Tracks details about the device, including its type, brand, model, and serial number.
    Each device can optionally be associated with a customer and may contain parts (e.g., RAM, SSD) added or replaced during repairs.
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices", null=True, blank=True)
    device_type = models.CharField(max_length=100, choices=Devices.DEVICE_TYPES, default=Devices.LAPTOP)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    repair_status = models.CharField(
        max_length=20,
        choices=Devices.DEVICE_REPAIR_STATUSES,
        default=Devices.IN_PROGRESS,
        null=True,
        blank=True
    )
    sale_status = models.CharField(
        max_length=20,
        choices=Devices.DEVICE_SALE_STATUSES,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_type} - {self.model} ({self.customer.username})"


class DevicePart(models.Model):
    """
    Represents individual parts or admin of a device, such as a motherboard, RAM, or hard drive.
    Each part can either be a standalone spare part in inventory stock or tied to a specific customer-owned device.
    Tracks essential details such as name, model, serial number, price, stock quantity, warranty period, and part status (e.g., in stock, used, or out of stock).
    """
    customer_laptop = models.ForeignKey(Device, on_delete=models.SET_NULL, related_name="parts", blank=True, null=True)
    name = models.CharField(
        max_length=100,
        help_text="Name of the part e.g.: 16GB DDR4 RAM, 256GB NVMe SSD, or even the accompanying bag"
    )
    model = models.CharField(max_length=100, help_text="Model number or Brand of the part")
    serial_number = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField(
        default=0,
        null=True,
        help_text="Number of parts in stock or those which came with the device"
    )
    status = models.CharField(max_length=20, choices=DeviceParts.DEVICE_PARTS_STATUSES, null=True, blank=True)
    warranty_months = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.model} ({'Standalone' if not self.customer_laptop else self.customer_laptop.model})"


class PartMovement(models.Model):
    """
    Tracks the movement of device parts within inventory, such as when parts are added, removed, or transferred.
    Each entry specifies the part involved, the quantity moved, the type of movement (e.g., "In Stock," "Used"), and any relevant notes.
    Also records the user responsible for logging the movement.
    """
    part = models.ForeignKey(DevicePart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=DeviceParts.MOVEMENT_TYPES)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)


class DeviceRepairHistory(models.Model):
    """
    Records the repair history of a specific customer device, including the associated booking, technician, and diagnosis.
    Tracks parts that were replaced during the repair and provides a timestamp of when the repair was completed.
    Used for maintaining a detailed history of serviced devices for future reference.
    """
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.SET_NULL, null=True)
    diagnosis = models.TextField()
    parts_replaced = models.ManyToManyField(DevicePart)
    repair_date = models.DateTimeField(auto_now_add=True)
    technician = models.ForeignKey('accounts.StaffProfile', on_delete=models.SET_NULL, null=True)
