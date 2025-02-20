# apps/accounts/permissions.py
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsCustomerUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and hasattr(request.user, 'customer_profile'))
