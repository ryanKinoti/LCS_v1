from rest_framework import serializers

from apps.bookings.models import Booking


class BookingMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for booking references in other serializers.
    """

    class Meta:
        model = Booking
        fields = ['id', 'job_card_number', 'status', 'scheduled_time', 'payment_status']
