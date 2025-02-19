# apps/finances/serializers.py
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from decimal import Decimal

from .models import Transaction, PaymentRecord, FinancialSummary
from apps.accounts.serializers import UserMinimalSerializer
from utils.constants import Finances


class TransactionMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal representation of transactions for nested relationships.
    """

    class Meta:
        model = Transaction
        fields = ['id', 'reference_number', 'amount', 'status', 'created_at']


class PaymentRecordMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal representation of payment records for nested relationships.
    """

    class Meta:
        model = PaymentRecord
        fields = ['id', 'amount_paid', 'payment_date', 'receipt_number']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new transactions with proper validation and
    content type handling.
    """
    content_type_name = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Transaction
        fields = [
            'content_type_name', 'object_id', 'transaction_type',
            'amount', 'payment_method', 'notes'
        ]

    def validate_transaction_type(self, value):
        """Validate transaction type based on content object"""
        content_type = self.validated_data.get('content_type')
        if content_type:
            valid_types = {
                'booking': [Finances.BOOKING_PAYMENT, Finances.SERVICE_PAYMENT, Finances.REFUNDED],
                'device_part': [Finances.PARTS_PURCHASE, Finances.SERVICE_PAYMENT],
                'staff_profile': [Finances.STAFF_SALARY]
            }
            allowed_types = valid_types.get(content_type.model, [])
            if value not in allowed_types:
                raise serializers.ValidationError(
                    f"Invalid transaction type for {content_type.model}"
                )
        return value

    def validate(self, data):
        """Validate transaction data and content type."""
        try:
            content_type = ContentType.objects.get(model=data['content_type_name'].lower())
            data['content_type'] = content_type
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(
                f"Invalid content type: {data['content_type_name']}"
            )

        # Validate amount is positive
        if data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")

        # Ensure related object exists
        try:
            related_object = content_type.get_object_for_this_type(id=data['object_id'])
        except:
            raise serializers.ValidationError(
                f"No {data['content_type_name']} found with id {data['object_id']}"
            )

        # Remove write-only fields before saving
        data.pop('content_type_name')
        return data


class PaymentRecordCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new payment records with validation for
    payment amounts and transaction status updates.
    """

    class Meta:
        model = PaymentRecord
        fields = [
            'transaction', 'amount_paid', 'payment_method',
            'receipt_number', 'notes'
        ]

    def validate(self, data):
        """
        Validate payment amount against transaction balance and
        ensure unique receipt numbers.
        """
        transaction = data['transaction']
        amount_paid = data['amount_paid']

        # Calculate remaining balance
        total_paid = transaction.payments.aggregate(
            total=Sum('amount_paid')
        )['total'] or Decimal('0')
        remaining = transaction.amount - total_paid

        if amount_paid > remaining:
            raise serializers.ValidationError(
                f"Payment amount ({amount_paid}) exceeds remaining balance ({remaining})"
            )

        if PaymentRecord.objects.filter(receipt_number=data['receipt_number']).exists():
            raise serializers.ValidationError("Receipt number already exists")

        return data

    def create(self, validated_data):
        """Create payment record and update transaction status if fully paid."""
        payment = super().create(validated_data)
        transaction = payment.transaction

        # Calculate if transaction is fully paid
        total_paid = transaction.payments.aggregate(
            total=Sum('amount_paid')
        )['total'] or Decimal('0')

        if total_paid >= transaction.amount:
            transaction.status = Finances.PAID
            transaction.save()

        return payment


class TransactionDetailSerializer(serializers.ModelSerializer):
    """
    Detailed transaction serializer with related payments and
    created_by information.
    """
    created_by = UserMinimalSerializer(read_only=True)
    payments = PaymentRecordMinimalSerializer(many=True, read_only=True)
    related_object_type = serializers.SerializerMethodField()
    related_object_detail = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference_number', 'transaction_type', 'amount',
            'status', 'payment_method', 'notes', 'created_by',
            'created_at', 'updated_at', 'payments',
            'related_object_type', 'related_object_detail'
        ]

    def get_related_object_type(self, obj):
        """Get the type of related object (e.g., 'booking', 'inventory')."""
        return obj.content_type.model

    def get_related_object_detail(self, obj):
        """Get basic details of the related object."""
        related_object = obj.content_object
        if not related_object:
            return None

        # Basic information based on object type
        if obj.content_type.model == 'booking':
            return {
                'id': related_object.id,
                'job_card_number': related_object.job_card_number,
                'customer_name': related_object.customer.user.get_full_name()
            }
        elif obj.content_type.model == 'devicepart':
            return {
                'id': related_object.id,
                'name': related_object.name,
                'model': related_object.model
            }
        return {'id': related_object.id}


class PaymentRecordDetailSerializer(serializers.ModelSerializer):
    """
    Detailed payment record serializer with transaction and
    recorder information.
    """
    recorded_by = UserMinimalSerializer(read_only=True)
    transaction = TransactionMinimalSerializer(read_only=True)

    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'transaction', 'amount_paid', 'payment_date',
            'payment_method', 'receipt_number', 'recorded_by',
            'notes'
        ]


class FinancialSummarySerializer(serializers.ModelSerializer):
    """
    Serializer for financial summaries with calculated fields
    for financial analysis.
    """
    net_revenue = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()

    class Meta:
        model = FinancialSummary
        fields = [
            'id', 'date', 'total_revenue', 'total_expenses',
            'service_revenue', 'parts_revenue', 'outstanding_payments',
            'net_revenue', 'profit_margin'
        ]

    def get_net_revenue(self, obj):
        """Calculate net revenue (total revenue - total expenses)."""
        return obj.total_revenue - obj.total_expenses

    def get_profit_margin(self, obj):
        """Calculate profit margin as a percentage."""
        if obj.total_revenue == 0:
            return 0
        net_revenue = obj.total_revenue - obj.total_expenses
        return round((net_revenue / obj.total_revenue) * 100, 2)
