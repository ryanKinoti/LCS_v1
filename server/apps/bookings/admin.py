from django.contrib import admin
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from .models import Booking, BookingParts


class BookingPartsInline(admin.TabularInline):
    """
    Inline admin for managing parts associated with a booking.
    Provides a convenient interface for adding and managing parts directly
    within the booking detail view, with stock validation and clear display
    of part information.
    """
    model = BookingParts
    extra = 1
    fields = ('part', 'quantity', 'get_stock_status', 'get_part_price')
    readonly_fields = ('get_stock_status', 'get_part_price')

    def get_stock_status(self, obj):
        """Display the current stock status of the part with color coding"""
        if not obj or not obj.part:
            return "-"

        if obj.part.customer_laptop:
            return format_html(
                '<span style="color: purple;">Customer Device Part</span>'
            )

        available = obj.part.quantity
        if available <= 0:
            return format_html(
                '<span style="color: red;">Out of Stock</span>'
            )
        elif available < obj.part.minimum_stock:
            return format_html(
                '<span style="color: orange;">Low Stock: {}</span>',
                available
            )
        return format_html(
            '<span style="color: green;">In Stock: {}</span>',
            available
        )

    get_stock_status.short_description = 'Stock Status'

    def get_part_price(self, obj):
        """Display the part price with currency formatting"""
        if not obj or not obj.part or not obj.part.price:
            return "-"
        return format_html(
            'KES {0}',
            '{:,.2f}'.format(obj.part.price)
        )

    get_part_price.short_description = 'Unit Price'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Admin interface for managing service bookings. Provides comprehensive booking
    management with status tracking, financial information, and appointment scheduling.
    Includes validation for business hours and technician availability.
    """
    list_display = (
        'job_card_number', 'get_customer_info', 'get_service_info', 'get_scheduled_time', 'get_status_badge',
        'get_payment_status', 'get_total_amount', 'get_parts_summary')
    readonly_fields = ('created_at', 'updated_at', 'total_parts_cost', 'get_parts_details')
    list_filter = (
        'status',
        'payment_status',
        'is_active',
        'scheduled_time',
        'technician',
        'detailed_service__device'
    )
    search_fields = (
        'customer__user__username',
        'customer__user__first_name',
        'customer__user__last_name',
        'device__serial_number',
        'detailed_service__service__name',
        'notes',
        'diagnosis'
    )
    inlines = [BookingPartsInline]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'customer',
                'technician',
                'detailed_service',
                'device',
                'scheduled_time'
            )
        }),
        ('Status Information', {
            'fields': (
                'status',
                'is_active',
                'payment_status'
            )
        }),
        ('Parts and Financial Details', {
            'fields': (
                'get_parts_details',
                'total_parts_cost',
            )
        }),
        ('Additional Information', {
            'fields': (
                'notes',
                'diagnosis'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )

    def get_parts_summary(self, obj):
        """Display a summary of parts in the list view"""
        parts_count = obj.bookingparts_set.count()
        if parts_count == 0:
            return format_html('<span style="color: gray;">No parts</span>')

        return format_html(
            '<span style="color: blue;">{} part{}</span>',
            parts_count,
            's' if parts_count > 1 else ''
        )

    get_parts_summary.short_description = 'Parts'

    def get_parts_details(self, obj):
        """Display detailed parts information in the detail view"""
        parts = obj.bookingparts_set.all()
        if not parts:
            return format_html('<span style="color: gray;">No parts assigned to this booking</span>')

        parts_html = ['<table style="width: 100%;">', '<tr>',
                      '<th style="padding: 8px;">Part Name</th>', '<th style="padding: 8px;">Quantity</th>',
                      '<th style="padding: 8px;">Unit Price</th>', '<th style="padding: 8px;">Total</th>', '</tr>']

        for booking_part in parts:
            part = booking_part.part
            total = part.price * booking_part.quantity if part.price else 0

            parts_html.append('<tr>')
            parts_html.append(f'<td style="padding: 8px;">{part.name}</td>')
            parts_html.append(f'<td style="padding: 8px;">{booking_part.quantity}</td>')
            parts_html.append(
                f'<td style="padding: 8px;">KES {"{:,.2f}".format(part.price) if part.price else "N/A"}</td>'
            )
            parts_html.append(f'<td style="padding: 8px;">KES {"{:,.2f}".format(total)}</td>')
            parts_html.append('</tr>')

        parts_html.append('</table>')
        return format_html(''.join(parts_html))

    get_parts_details.short_description = 'Parts Details'

    def get_customer_info(self, obj):
        """Display customer information with a link to their profile"""
        if obj.customer and obj.customer.user:
            user = obj.customer.user
            full_name = user.get_full_name() or user.username
            url = reverse('admin:accounts_customerprofile_change', args=[obj.customer.id])
            return format_html(
                '<a href="{}" title="View customer profile">{}</a>',
                url,
                full_name
            )
        return "No customer assigned"

    get_customer_info.short_description = 'Customer'

    def get_service_info(self, obj):
        """Display service information with estimated duration"""
        if obj.detailed_service:
            service = obj.detailed_service.service
            duration = service.estimated_time
            hours = int(duration.total_seconds() // 3600)
            minutes = int((duration.total_seconds() % 3600) // 60)
            return format_html(
                '{} <br><small>({} h {} m)</small>',
                obj.detailed_service,
                hours,
                minutes
            )
        return "No service selected"

    get_service_info.short_description = 'Service'

    def get_scheduled_time(self, obj):
        """Display scheduled time with color coding for past/future appointments"""
        if not obj.scheduled_time:
            return "-"

        now = timezone.now()
        time_diff = obj.scheduled_time - now

        if time_diff.total_seconds() < 0:
            color = 'red'
            label = 'Past'
        elif time_diff.total_seconds() < 24 * 60 * 60:
            color = 'orange'
            label = 'Today'
        else:
            color = 'green'
            label = 'Future'

        return format_html(
            '<span style="color: {}">{}</span><br><small>{}</small>',
            color,
            obj.scheduled_time.strftime('%Y-%m-%d %H:%M'),
            label
        )

    get_scheduled_time.short_description = 'Scheduled Time'

    def get_status_badge(self, obj):
        """Display booking status with appropriate color coding"""
        status_colors = {
            'pending': 'orange',
            'confirmed': 'blue',
            'in_progress': 'purple',
            'completed': 'green',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.status.lower(), 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 10px;">{}</span>',
            color,
            obj.get_status_display()
        )

    get_status_badge.short_description = 'Status'

    def get_payment_status(self, obj):
        """Display payment status with color coding"""
        status_colors = {
            'pending': 'orange',
            'partial': 'blue',
            'paid': 'green',
            'refunded': 'red'
        }
        color = status_colors.get(obj.payment_status.lower(), 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_payment_status_display()
        )

    get_payment_status.short_description = 'Payment'

    def get_total_amount(self, obj):  # Replace this method
        """Calculate and display the total booking amount"""
        service_price = obj.detailed_service.price if obj.detailed_service else 0
        total = service_price + obj.total_parts_cost
        return format_html(
            'KES {0}',
            '{:,.2f}'.format(total)
        )

    get_total_amount.short_description = 'Total Amount'

    def save_model(self, request, obj, form, change):
        """Override save_model to update total_parts_cost when booking is saved"""
        super().save_model(request, obj, form, change)
        # Recalculate total parts cost
        total_cost = sum(
            bp.part.price * bp.quantity
            for bp in obj.bookingparts_set.all()
            if bp.part.price
        )
        if total_cost != obj.total_parts_cost:
            obj.total_parts_cost = total_cost
            obj.save(update_fields=['total_parts_cost'])
