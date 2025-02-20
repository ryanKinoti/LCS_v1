from django.contrib import admin
from django.utils.html import format_html
from .models import Device, DevicePart, PartMovement, DeviceRepairHistory


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """
    Admin configuration for Device model.
    Provides a comprehensive interface for managing customer devices with custom display
    and filtering options.
    """
    list_display = (
        'device_type',
        'brand',
        'model',
        'serial_number',
        'price',
        'get_customer_name',
        'repair_status',
        'sale_status',
        'created_at'
    )
    list_filter = ('device_type', 'repair_status', 'sale_status', 'brand')
    search_fields = ('serial_number', 'brand', 'model', 'customer__username', 'customer__email')
    readonly_fields = ('created_at',)

    # Organize fields into logical groups
    fieldsets = (
        ('Device Information', {
            'fields': ('device_type', 'brand', 'model', 'serial_number', 'price')
        }),
        ('Status Information', {
            'fields': ('repair_status', 'sale_status')
        }),
        ('Customer Information', {
            'fields': ('customer',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def get_customer_name(self, obj):
        """Display customer's full name if available, otherwise show 'No Customer'"""
        if obj.customer:
            return f"{obj.customer.get_full_name() or obj.customer.username}"
        return "No Customer"

    get_customer_name.short_description = 'Customer'


@admin.register(DevicePart)
class DevicePartAdmin(admin.ModelAdmin):
    """
    Admin configuration for DevicePart model.
    Provides inventory management interface with stock level indicators and
    advanced filtering options.
    """
    list_display = (
        'name',
        'model',
        'serial_number',
        'customer_laptop',
        'get_price',
        'get_stock_status',
        'status',
        'warranty_months'
    )
    list_filter = ('status', 'warranty_months')
    search_fields = ('name', 'model', 'serial_number', 'customer_laptop__serial_number')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Part Information', {
            'fields': ('name', 'model', 'serial_number')
        }),
        ('Inventory Details', {
            'fields': ('price', 'quantity', 'status', 'minimum_stock')
        }),
        ('Device Association', {
            'fields': ('customer_laptop',)
        }),
        ('Warranty Information', {
            'fields': ('warranty_months',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

    def get_price(self, obj):
        """Display formatted price with currency symbol"""
        return f"${obj.price}" if obj.price else "N/A"

    get_price.short_description = 'Price'

    def get_stock_status(self, obj):
        """
        Display color-coded stock status based on quantity and minimum stock levels
        """
        if obj.quantity is None:
            return format_html('<span style="color: gray;">N/A</span>')

        if obj.quantity <= 0:
            color = 'red'
            status = 'Out of Stock'
        elif obj.quantity < obj.minimum_stock:
            color = 'orange'
            status = f'Low Stock ({obj.quantity})'
        else:
            color = 'green'
            status = f'In Stock ({obj.quantity})'

        return format_html('<span style="color: {};">{}</span>', color, status)

    get_stock_status.short_description = 'Stock Status'


@admin.register(PartMovement)
class PartMovementAdmin(admin.ModelAdmin):
    """
    Admin configuration for PartMovement model.
    Tracks and displays inventory movement history with detailed filtering
    and search capabilities.
    """
    list_display = (
        'part',
        'quantity',
        'movement_type',
        'created_by',
        'created_at'
    )
    list_filter = ('movement_type', 'created_at', 'created_by')
    search_fields = ('part__name', 'part__serial_number', 'notes', 'created_by__username')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Movement Details', {
            'fields': ('part', 'quantity', 'movement_type')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(DeviceRepairHistory)
class DeviceRepairHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for DeviceRepairHistory model.
    Provides a comprehensive view of repair history with related device
    and technician information.
    """
    list_display = (
        'device',
        'get_device_serial',
        'get_technician_name',
        'repair_date'
    )
    list_filter = ('repair_date', 'technician')
    search_fields = (
        'device__serial_number',
        'device__model',
        'diagnosis',
        'technician__user__username'
    )
    readonly_fields = ('repair_date',)

    fieldsets = (
        ('Repair Information', {
            'fields': ('device', 'booking', 'technician')
        }),
        ('Technical Details', {
            'fields': ('diagnosis', 'parts_replaced')
        }),
        ('Timestamps', {
            'fields': ('repair_date',),
            'classes': ('collapse',)
        })
    )

    def get_device_serial(self, obj):
        """Display device serial number"""
        return obj.device.serial_number

    get_device_serial.short_description = 'Serial Number'

    def get_technician_name(self, obj):
        """Display technician's full name if available"""
        if obj.technician and obj.technician.user:
            return obj.technician.user.get_full_name() or obj.technician.user.username
        return "No Technician Assigned"

    get_technician_name.short_description = 'Technician'
