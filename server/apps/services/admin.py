from django.contrib import admin
from django.utils.html import format_html
from .models import ServiceCategory, Service, DetailedService, ServicePartsRequired


class ServiceInline(admin.TabularInline):
    """
    Inline admin for Service model, allowing services to be managed directly
    within their respective category pages. This makes it easier to organize
    and manage related services together.
    """
    model = Service
    extra = 1  # Number of empty forms to display
    fields = ('name', 'estimated_time', 'active')
    show_change_link = True  # Allows quick navigation to the service's detailed view


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for service categories. Provides a clear overview of available
    service categories and their associated services through the inline integration.
    The interface emphasizes easy category management and service organization.
    """
    list_display = ('name', 'get_service_count', 'get_description_preview')
    search_fields = ('name', 'description')
    inlines = [ServiceInline]

    def get_service_count(self, obj):
        """Display the number of services in each category"""
        count = obj.services.count()
        return format_html(
            '<span style="color: {}">{} Service{}</span>',
            'green' if count > 0 else 'red',
            count,
            's' if count != 1 else ''
        )

    get_service_count.short_description = 'Services'

    def get_description_preview(self, obj):
        """Show a truncated version of the description for quick overview"""
        if obj.description:
            return (obj.description[:75] + '...') if len(obj.description) > 75 else obj.description
        return "No description provided"

    get_description_preview.short_description = 'Description Preview'


class DetailedServiceInline(admin.StackedInline):
    """
    Inline admin for DetailedService model. Uses StackedInline for better
    visibility of the multiple fields associated with each detailed service.
    Allows direct management of detailed services within the main service view.
    """
    model = DetailedService
    extra = 1
    fields = (('device', 'price'), 'changes_to_make', 'notes')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Admin interface for services. Provides comprehensive service management
    with status indicators, filtering options, and integrated detailed service
    management through inline admin classes.
    """
    list_display = (
        'name',
        'category',
        'get_estimated_time',
        'get_status',
        'get_detailed_services_count'
    )
    list_filter = ('active', 'category', 'estimated_time')
    search_fields = ('name', 'description', 'category__name')
    inlines = [DetailedServiceInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category')
        }),
        ('Service Details', {
            'fields': ('description', 'estimated_time', 'active')
        })
    )

    def get_estimated_time(self, obj):
        """Format the estimated time in a human-readable format"""
        hours = obj.estimated_time.total_seconds() // 3600
        minutes = (obj.estimated_time.total_seconds() % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"

    get_estimated_time.short_description = 'Est. Time'

    def get_status(self, obj):
        """Display the service status with appropriate color coding"""
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.active else 'red',
            'Active' if obj.active else 'Inactive'
        )

    get_status.short_description = 'Status'

    def get_detailed_services_count(self, obj):
        """Show the number of detailed services associated with this service"""
        count = obj.details.count()
        return format_html(
            '<span title="Number of detailed service variations">{}</span>',
            count
        )

    get_detailed_services_count.short_description = 'Variations'


class ServicePartsRequiredInline(admin.TabularInline):
    """
    Inline admin for ServicePartsRequired model. Allows direct management
    of required parts within the detailed service view for streamlined
    service configuration.
    """
    model = ServicePartsRequired
    extra = 1
    fields = ('part_type', 'quantity', 'mandatory')


@admin.register(DetailedService)
class DetailedServiceAdmin(admin.ModelAdmin):
    """
    Admin interface for detailed services. Provides comprehensive management
    of specific service variations including required parts, pricing, and
    device-specific details.
    """
    list_display = (
        'service',
        'device',
        'get_formatted_price',
        'get_required_parts_count'
    )
    list_filter = ('device', 'service__category', 'service__active')
    search_fields = (
        'service__name',
        'changes_to_make',
        'notes'
    )
    inlines = [ServicePartsRequiredInline]

    fieldsets = (
        ('Service Information', {
            'fields': ('service', 'device')
        }),
        ('Details', {
            'fields': ('changes_to_make', 'price', 'notes')
        })
    )

    def get_formatted_price(self, obj):
        """Display the price with currency formatting"""
        return format_html('KES {:,.2f}', obj.price)

    get_formatted_price.short_description = 'Price'

    def get_required_parts_count(self, obj):
        """Show the number of required parts for this service"""
        required_parts = ServicePartsRequired.objects.filter(detailed_service=obj)
        mandatory_count = sum(1 for part in required_parts if part.mandatory)
        optional_count = sum(1 for part in required_parts if not part.mandatory)

        return format_html(
            '<span title="Mandatory: {} | Optional: {}">{} part{}</span>',
            mandatory_count,
            optional_count,
            mandatory_count + optional_count,
            's' if (mandatory_count + optional_count) != 1 else ''
        )

    get_required_parts_count.short_description = 'Required Parts'
