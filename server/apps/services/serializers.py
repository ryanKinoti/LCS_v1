# apps/services/serializers.py
from rest_framework import serializers
from .models import ServiceCategory, Service, DetailedService, ServicePartsRequired
from apps.inventory.serializers import DevicePartMinimalSerializer


class ServiceCategoryMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal representation of service categories, used primarily for nested relationships
    and list views where complete details aren't necessary.
    """

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name']


class ServiceMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal representation of services, used for nested relationships and quick reference.
    Includes only the essential fields needed for basic service identification.
    """

    class Meta:
        model = Service
        fields = ['id', 'name', 'estimated_time']


class DetailedServiceMinimalSerializer(serializers.ModelSerializer):
    """
    A minimal representation of detailed services, used when referencing from other models
    like bookings or when listing services in a compact format.
    """
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = DetailedService
        fields = ['id', 'service_name', 'device', 'price']


class ServicePartsRequiredSerializer(serializers.ModelSerializer):
    """
    Handles the creation and display of parts required for a detailed service.
    Includes validation for part quantities and provides part details when needed.
    """
    part_details = DevicePartMinimalSerializer(source='part_type', many=True, read_only=True)

    class Meta:
        model = ServicePartsRequired
        fields = ['id', 'part_type', 'part_details', 'quantity', 'mandatory']

    def validate_quantity(self, value):
        """Ensure quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero")
        return value


class ServiceCategoryCreateSerializer(serializers.ModelSerializer):
    """
    Dedicated serializer for creating and updating service categories.
    Includes validation for unique category names.
    """

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description']

    def validate_name(self, value):
        """Ensure category name is unique (case-insensitive)."""
        if ServiceCategory.objects.filter(name__iexact=value).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("A service category with this name already exists")
        return value


class ServiceCreateSerializer(serializers.ModelSerializer):
    """
    Handles the creation and updating of services with comprehensive validation.
    Ensures proper category assignment and time format validation.
    """

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'description', 'estimated_time', 'active']

    def validate_name(self, value):
        """Ensure service name is unique within its category."""
        category_id = self.initial_data.get('category')
        if Service.objects.filter(
                name__iexact=value,
                category_id=category_id
        ).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError("A service with this name already exists in this category")
        return value


class DetailedServiceCreateSerializer(serializers.ModelSerializer):
    """
    Manages the creation and updating of detailed services.
    Includes validation for price and ensures proper service-device combinations.
    """

    class Meta:
        model = DetailedService
        fields = ['id', 'service', 'device', 'changes_to_make', 'price', 'notes']

    def validate(self, data):
        """Validate unique service-device combination and ensure positive price."""
        if DetailedService.objects.filter(
                service=data['service'],
                device=data['device']
        ).exclude(id=getattr(self.instance, 'id', None)).exists():
            raise serializers.ValidationError(
                "A detailed service for this device and service combination already exists"
            )

        if data['price'] <= 0:
            raise serializers.ValidationError("Price must be greater than zero")

        return data


class ServiceCategoryDetailSerializer(serializers.ModelSerializer):
    """
    Provides a complete view of a service category including all its services.
    Used for detailed category views and service browsing.
    """
    services = ServiceMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'services']


class ServiceDetailSerializer(serializers.ModelSerializer):
    """
    Comprehensive service representation including category and detailed services.
    Used for service management and detailed service views.
    """
    category = ServiceCategoryMinimalSerializer(read_only=True)
    details = DetailedServiceMinimalSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'description', 'estimated_time', 'active', 'details']


class DetailedServiceDetailSerializer(serializers.ModelSerializer):
    """
    Complete detailed service representation including service information and required parts.
    Used for service configuration and management interfaces.
    """
    service = ServiceMinimalSerializer(read_only=True)
    parts_required = serializers.SerializerMethodField()

    class Meta:
        model = DetailedService
        fields = [
            'id', 'service', 'device', 'changes_to_make',
            'price', 'notes', 'parts_required'
        ]

    def get_parts_required(self, obj):
        """Retrieve and format required parts information."""
        parts = ServicePartsRequired.objects.filter(detailed_service=obj)
        return ServicePartsRequiredSerializer(parts, many=True).data
