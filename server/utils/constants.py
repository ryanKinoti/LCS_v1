# server/utils/constants.py
from django.utils.translation import gettext_lazy as _


class Devices:
    LAPTOP = 'laptop'
    DESKTOP = 'desktop'
    PRINTER = 'printer'

    COMPLETED = "completed"
    RETURNED = "returned"
    IN_PROGRESS = "in_progress"

    NEW = "new"
    SOLD = "sold"
    REFURBISHED = "refurbished"

    DEVICE_TYPES = [
        (LAPTOP, _('Laptop')),
        (DESKTOP, _('Desktop')),
        (PRINTER, _('Printer')),
    ]

    DEVICE_REPAIR_STATUSES = [
        (COMPLETED, _('Completed')),
        (RETURNED, _('Returned')),
        (IN_PROGRESS, _('In Progress')),
    ]

    DEVICE_SALE_STATUSES = [
        (NEW, _('New')),
        (SOLD, _('Sold')),
        (REFURBISHED, _('Refurbished')),
    ]


class DeviceParts:
    IN_STOCK = "in_stock"
    OUT_OF_STOCK = "out_of_stock"
    USED = "used"
    DEFECTIVE = "defective"
    DISPOSED = "disposed"

    REPAIR = "repair"
    SALE = "sale"

    DEVICE_PARTS_STATUSES = [
        (IN_STOCK, _('In Stock')),
        (OUT_OF_STOCK, _('Out of Stock')),
        (USED, _('Used')),
        (DEFECTIVE, _('Defective')),
        (DISPOSED, _('Disposed')),
    ]

    MOVEMENT_TYPES = [
        (REPAIR, _('Used in Repair')),
        (SALE, _('Used in a Sale')),
    ]


class BookingStatus:
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'canceled'

    CHOICES = [
        (PENDING, _('Pending')),
        (CONFIRMED, _('Confirmed')),
        (IN_PROGRESS, _('In Progress')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
    ]


class Finances:
    PENDING = 'pending'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'

    BOOKING_PAYMENT = 'booking_payment'
    PARTS_PURCHASE = 'parts_purchase'
    SERVICE_PAYMENT = 'service_payment'
    STAFF_SALARY = 'staff_salary'

    CASH = 'cash'
    CARD = 'card'
    MPESA = 'mpesa'
    BANK_TRANSFER = 'bank_transfer'

    CHOICES = [
        (PENDING, _('Pending')),
        (PAID, _('Paid')),
        (FAILED, _('Failed')),
        (REFUNDED, _('Refunded')),
    ]

    TRANSACTION_TYPES = [
        (BOOKING_PAYMENT, _('Booking Payment')),
        (PARTS_PURCHASE, _('Parts Purchase')),
        (SERVICE_PAYMENT, _('Service Payment')),
        (STAFF_SALARY, _('Staff Salary')),
    ]

    PAYMENT_METHODS = [
        (CASH, _('Cash')),
        (CARD, _('Card')),
        (MPESA, _('M-Pesa')),
        (BANK_TRANSFER, _('Bank Transfer')),
    ]


class UserRoles:
    CLIENT = 'client'
    COMPANY = 'company'
    TECHNICIAN = 'technician'
    ADMIN = 'admin'
    RECEPTIONIST = 'receptionist'

    CUSTOMER_ROLES = [
        (CLIENT, _('Client')),
        (COMPANY, _('Company')),
    ]
    STAFF_ROLES = [
        (TECHNICIAN, _('Technician')),
        (ADMIN, _('Admin')),
        (RECEPTIONIST, _('Receptionist')),
    ]


class ContactMethods:
    EMAIL = 'email'
    PHONE_CALL = 'phone_call'
    SMS = 'sms'

    CHOICES = [
        (EMAIL, _('Email')),
        (PHONE_CALL, _('Phone Call')),
        (SMS, _('SMS')),
    ]


BUSINESS_HOURS = {
    'start_time': '08:00 AM',
    'end_time': '06:00 PM',
}
