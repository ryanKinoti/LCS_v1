# apps/accounts/serializers/dashboard.py
from datetime import timedelta

from django.db.models import Q, F
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import StaffProfile
from apps.accounts.serializers import StaffProfileSerializer, StaffProfileMinimalSerializer
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingDetailSerializer, BookingMinimalSerializer
from apps.finances.models import Transaction, FinancialSummary
from apps.finances.serializers import TransactionDetailSerializer, FinancialSummarySerializer
from apps.inventory.models import DevicePart, DeviceRepairHistory
from apps.inventory.serializers import DevicePartDetailSerializer, DevicePartMinimalSerializer, \
    DeviceRepairHistoryDetailSerializer
from apps.services.models import Service, ServiceCategory
from apps.services.serializers import ServiceDetailSerializer, ServiceCategoryDetailSerializer
from utils.constants import BookingStatus, Finances


class AdminDashboardSerializer(serializers.Serializer):
    """
    Comprehensive serializer for admin dashboard data.
    Aggregates data from all relevant models to provide a complete overview.
    """
    # Overview statistics
    total_repairs = serializers.IntegerField()
    pending_repairs = serializers.IntegerField()
    completed_repairs = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_staff = serializers.IntegerField()

    def to_representation(self, instance):
        """
        Transform the data into the required format with all necessary calculations.
        """
        # Time ranges
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        repair_stats = self._get_repair_statistics(thirty_days_ago)
        inventory_stats = self._get_inventory_statistics()
        staff_stats = self._get_staff_statistics(thirty_days_ago)
        financial_stats = self._get_financial_statistics(thirty_days_ago)
        service_stats = self._get_service_statistics(thirty_days_ago)
        recent_activities = self._get_recent_activities()
        return {
            'repair_statistics': repair_stats,
            'inventory_overview': inventory_stats,
            'staff_overview': staff_stats,
            'financial_metrics': financial_stats,
            'service_metrics': service_stats,
            'recent_activities': recent_activities,
        }

    def _get_repair_statistics(self, since_date):
        """Aggregates repair statistics using BookingDetailSerializer"""
        bookings = Booking.objects.filter(created_at__gte=since_date)
        serialized_bookings = BookingDetailSerializer(bookings, many=True).data

        stats = {
            'total_repairs': len(serialized_bookings),
            'status_breakdown': {},
            'recent_bookings': BookingMinimalSerializer(
                bookings.order_by('-created_at')[:5],
                many=True
            ).data
        }

        for booking in serialized_bookings:
            status = booking['status']
            stats['status_breakdown'][status] = stats['status_breakdown'].get(status, 0) + 1

        return stats

    def _get_inventory_statistics(self):
        """Aggregates inventory statistics using DevicePartDetailSerializer"""
        low_stock_parts = DevicePart.objects.filter(
            Q(quantity__lte=F('minimum_stock')) &
            Q(customer_laptop__isnull=True)
        )
        return {
            'low_stock_items': DevicePartDetailSerializer(
                low_stock_parts,
                many=True
            ).data,
            'total_parts': DevicePartMinimalSerializer(
                DevicePart.objects.all(),
                many=True
            ).data
        }

    def _get_staff_statistics(self, since_date):
        """Aggregates staff statistics using StaffProfileSerializer"""
        active_staff = StaffProfile.objects.filter(user__is_active=True)

        return {
            'active_staff': StaffProfileSerializer(
                active_staff,
                many=True
            ).data,
            'technician_stats': StaffProfileMinimalSerializer(
                active_staff.filter(role='technician'),
                many=True
            ).data
        }

    def _get_financial_statistics(self, since_date):
        """Aggregates financial statistics using TransactionDetailSerializer"""
        recent_transactions = Transaction.objects.filter(created_at__gte=since_date)

        return {
            'recent_transactions': TransactionDetailSerializer(
                recent_transactions,
                many=True
            ).data,
            'summary': FinancialSummarySerializer(
                FinancialSummary.objects.latest('date')
            ).data
        }

    def _get_service_statistics(self, since_date):
        """Aggregates service statistics using ServiceDetailSerializer"""
        active_services = Service.objects.filter(active=True)

        return {
            'available_services': ServiceDetailSerializer(
                active_services,
                many=True
            ).data,
            'categories': ServiceCategoryDetailSerializer(
                ServiceCategory.objects.all(),
                many=True
            ).data
        }

    def _calculate_revenue_data(self, start_date):
        """Calculate revenue metrics for the specified period."""
        completed_bookings = Booking.objects.filter(
            status=BookingStatus.COMPLETED,
            payment_status=Finances.PAID,
            created_at__gte=start_date
        )

        total_revenue = sum(
            booking.detailed_service.price + booking.total_parts_cost
            for booking in completed_bookings
        )

        return {
            'total_revenue': total_revenue,
            'bookings_count': completed_bookings.count(),
            'average_booking_value': total_revenue / completed_bookings.count() if completed_bookings.exists() else 0
        }

    def _get_recent_activities(self):
        """Compiles recent activities across all domains"""
        activities = []

        # Get recent bookings
        recent_bookings = Booking.objects.order_by('-created_at')[:5]
        activities.extend({
                              'type': 'booking',
                              'data': BookingMinimalSerializer(booking).data,
                              'timestamp': booking.created_at
                          } for booking in recent_bookings)

        # Get recent repairs
        recent_repairs = DeviceRepairHistory.objects.order_by('-repair_date')[:5]
        activities.extend({
                              'type': 'repair',
                              'data': DeviceRepairHistoryDetailSerializer(repair).data,
                              'timestamp': repair.repair_date
                          } for repair in recent_repairs)

        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)


class StaffDashboardSerializer(serializers.Serializer):
    assigned_repairs = serializers.IntegerField()
    pending_repairs = serializers.IntegerField()
    completed_repairs = serializers.IntegerField()


class CustomerDashboardSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
