# apps/services/models.py
from django.core.exceptions import ValidationError
from django.db import models

from apps.inventory.models import DevicePart
from utils.constants import Devices


class ServiceCategory(models.Model):
    """
    Represents a category or grouping of related services.
    For example, different types of repair services such as "Hardware Repairs" or "Software Upgrades."
    This model is primarily used for organizing services and allowing users to easily find services based on these categories.
    """
    name = models.CharField(max_length=100, unique=True, help_text="Name of the service category")
    description = models.TextField(blank=True, null=True, help_text="Optional description of the category")

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(models.Model):
    """
    Represents an individual repair or maintenance service offered by the business.
    For instance, "Screen Replacement" or "Battery Replacement."
    Each service belongs to a specific category (`ServiceCategory`) and includes details like estimated time, a description, and active status.
    """
    name = models.CharField(max_length=150, unique=True, help_text="Name of the service")
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name="services",
        help_text="Category of the service"
    )
    description = models.TextField(blank=True, null=True, help_text="Optional detailed description of this service")
    estimated_time = models.DurationField(help_text="Estimated completion time (hh:mm:ss)")
    active = models.BooleanField(default=True, help_text="Indicates if the service is currently active/available")

    class Meta:
        ordering = ["name"]  # Order services alphabetically
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.name


class DetailedService(models.Model):
    """
    Represents a more specific or customized breakdown of a service for a particular device type.
    For example, if the general service is "Screen Replacement," a detailed service could be "Screen Replacement for Galaxy S22."
    It includes details about the device, changes/repairs involved, pricing, and optional notes for further clarification.
    """
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="details", )
    device = models.CharField(
        max_length=100,
        choices=Devices.DEVICE_TYPES,
        help_text="Device undergoing repair or receiving the service (e.g., Laptop, Smartphone)"
    )
    changes_to_make = models.TextField(
        help_text="Description of the repair or change involved in this service e.g.: Adding RAM, Replacing screen. should begin with a verb"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the detailed service in KES")
    notes = models.TextField(blank=True, null=True, help_text="Additional information about a detailed service")

    class Meta:
        ordering = ["service", "device"]  # Order by service and device name
        verbose_name = "Detailed Service"
        verbose_name_plural = "Detailed Services"

    def __str__(self):
        return f"{self.service.name} - {self.device}"


class ServicePartsRequired(models.Model):
    """
    Represents a list of parts or part required to complete a specific detailed service.
    For example, for a detailed service like "Laptop Screen Replacement," it might include a required part such as "15.6-inch Screen."
    Tracks additional details like quantity and whether the part is mandatory for the service.
    """
    detailed_service = models.ForeignKey(DetailedService, on_delete=models.CASCADE)
    part_type = models.ManyToManyField(
        DevicePart,
        related_name="service_parts_required",
        help_text="Part(s) required for this service"
    )
    quantity = models.PositiveIntegerField(default=1)
    mandatory = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service Part Required"
        verbose_name_plural = "Service Parts Required"
        ordering = ["detailed_service", "part_type__name"]

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
