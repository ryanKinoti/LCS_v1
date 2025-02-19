from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.bookings.models import Booking
from .models import Transaction

@receiver(post_save, sender=Booking)
def create_booking_transaction(sender, instance, created, **kwargs):
    if created:
        # Calculate total amount including service and parts
        total_amount = instance.detailed_service.price + instance.total_parts_cost

        Transaction.objects.create(
            content_object=instance,
            transaction_type='booking_payment',
            amount=total_amount,
            status='pending',
            created_by=instance.customer.user
        )