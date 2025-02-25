# apps/accounts/serializers/dashboard.py
from datetime import timedelta, datetime

from django.db.models import Q, F, Count, Sum
from django.utils import timezone
from rest_framework import serializers

from apps.bookings.models import Booking
from apps.bookings.serializers import BookingDetailSerializer
from apps.finances.models import Transaction, FinancialSummary
from apps.finances.serializers import FinancialSummarySerializer, \
    FinancialSnapshotSerializer
from apps.inventory.models import DevicePart
from apps.inventory.serializers import DevicePartMinimalSerializer
from utils.constants import BookingStatus, Finances, DeviceParts


class AdminDashboardSerializer(serializers.Serializer):
    """
    Comprehensive serializer for admin dashboard data.
    Aggregates data from all relevant models to provide a complete overview.
    """
    active_bookings_count = serializers.IntegerField(read_only=True)
    pending_bookings_count = serializers.IntegerField(read_only=True)
    inventory_alerts_count = serializers.IntegerField(read_only=True)

    def to_representation(self, instance):
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        booking_stats = self._get_booking_statistics()
        inventory_alerts = self._get_inventory_alerts()
        financial_snapshot = self._get_financial_snapshot(seven_days_ago, now)
        recent_activities = self._get_recent_activities()

        return {
            'booking_statistics': booking_stats,
            'inventory_alerts': {
                'total_count': len(inventory_alerts),
                'items': inventory_alerts
            },
            'financial_snapshot': {
                'data': financial_snapshot,
                'summary': self._get_financial_summary()
            },
            'recent_activities': recent_activities
        }

    def _get_booking_statistics(self):
        active_statuses = [BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]
        booking_counts = Booking.objects.filter(is_active=True).values('status').annotate(
            count=Count('status')
        )
        counts_by_status = {item['status']: item['count'] for item in booking_counts}
        active_count = sum(counts_by_status.get(status, 0) for status in active_statuses)
        pending_count = counts_by_status.get(BookingStatus.PENDING, 0)
        completed_count = counts_by_status.get(BookingStatus.COMPLETED, 0)
        canceled_count = counts_by_status.get(BookingStatus.CANCELLED, 0)

        return {
            'active_bookings': active_count,
            'pending_bookings': pending_count,
            'completed_bookings': completed_count,
            'canceled_bookings': canceled_count,
            'total_bookings': active_count + pending_count + completed_count + canceled_count
        }

    def _get_inventory_alerts(self):
        low_stock_parts = DevicePart.objects.filter(
            Q(quantity__lte=F('minimum_stock')) &
            Q(customer_laptop__isnull=True) &
            ~Q(status=DeviceParts.OUT_OF_STOCK)  # Exclude already marked out-of-stock
        ).order_by('quantity')[:10]  # Limit to 10 most critical items

        return DevicePartMinimalSerializer(low_stock_parts, many=True).data

    def _get_financial_snapshot(self, start_date, end_date):
        date_range = []
        current_date = start_date.date()
        end_date = end_date.date()

        while current_date <= end_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)

        financial_data = []
        for date in date_range:  # Get transactions for this date
            day_start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(date, datetime.max.time()))

            # Calculate revenue (money coming in)
            revenue_transactions = Transaction.objects.filter(
                created_at__range=(day_start, day_end),
                transaction_type__in=[Finances.BOOKING_PAYMENT, Finances.SERVICE_PAYMENT],
                status__in=[Finances.PAID, Finances.PARTIAL]
            )

            # Calculate expenses (money going out)
            expense_transactions = Transaction.objects.filter(
                created_at__range=(day_start, day_end),
                transaction_type__in=[Finances.PARTS_PURCHASE, Finances.STAFF_SALARY]
            )

            total_revenue = revenue_transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            total_expenses = expense_transactions.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            net_income = total_revenue - total_expenses

            financial_data.append({
                'date': date,
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': net_income
            })

        return FinancialSnapshotSerializer(financial_data, many=True).data

    def _get_financial_summary(self):
        try:
            latest_summary = FinancialSummary.objects.latest('date')
            return FinancialSummarySerializer(latest_summary).data
        except FinancialSummary.DoesNotExist:
            return {
                'total_revenue': 0,
                'total_expenses': 0,
                'service_revenue': 0,
                'parts_revenue': 0,
                'outstanding_payments': 0,
                'net_revenue': 0,
                'profit_margin': 0
            }

    def _get_recent_activities(self):
        recent_bookings = Booking.objects.select_related(
            'customer__user',
            'technician__user',
            'detailed_service__service',
            'device'
        ).order_by('-created_at')[:10]

        return BookingDetailSerializer(recent_bookings, many=True).data


class StaffDashboardSerializer(serializers.Serializer):
    assigned_repairs = serializers.IntegerField()
    pending_repairs = serializers.IntegerField()
    completed_repairs = serializers.IntegerField()


class CustomerDashboardSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
