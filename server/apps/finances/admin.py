from django.contrib import admin
from django.utils.html import format_html
from .models import Transaction, PaymentRecord, FinancialSummary

class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 1
    readonly_fields = ('payment_date',)
    fields = ('amount_paid', 'payment_method', 'receipt_number', 'notes', 'payment_date')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'reference_number',
        'get_transaction_type',
        'get_amount',
        'get_status',
        'payment_method',
        'created_at'
    )
    list_filter = ('status', 'transaction_type', 'payment_method', 'created_at')
    search_fields = ('reference_number', 'notes', 'created_by__email')
    inlines = [PaymentRecordInline]
    readonly_fields = ('reference_number', 'created_at', 'updated_at')

    def get_transaction_type(self, obj):
        return obj.get_transaction_type_display()
    get_transaction_type.short_description = 'Type'

    def get_amount(self, obj):
        return format_html('KES {:,.2f}', obj.amount)
    get_amount.short_description = 'Amount'

    def get_status(self, obj):
        colors = {
            'pending': 'orange',
            'paid': 'green',
            'failed': 'red',
            'refunded': 'blue'
        }
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    get_status.short_description = 'Status'

@admin.register(FinancialSummary)
class FinancialSummaryAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'get_total_revenue',
        'get_total_expenses',
        'get_net_income',
        'get_outstanding_payments'
    )
    readonly_fields = ('date', 'total_revenue', 'total_expenses', 'service_revenue',
                       'parts_revenue', 'outstanding_payments')

    def get_total_revenue(self, obj):
        return format_html('KES {:,.2f}', obj.total_revenue)
    get_total_revenue.short_description = 'Total Revenue'

    def get_total_expenses(self, obj):
        return format_html('KES {:,.2f}', obj.total_expenses)
    get_total_expenses.short_description = 'Total Expenses'

    def get_net_income(self, obj):
        net_income = obj.total_revenue - obj.total_expenses
        color = 'green' if net_income >= 0 else 'red'
        return format_html(
            '<span style="color: {};">KES {:,.2f}</span>',
            color,
            net_income
        )
    get_net_income.short_description = 'Net Income'

    def get_outstanding_payments(self, obj):
        return format_html('KES {:,.2f}', obj.outstanding_payments)
    get_outstanding_payments.short_description = 'Outstanding Payments'