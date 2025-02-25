# apps/accounts/serializers/base.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

from ..models import CustomerProfile, StaffProfile

User = get_user_model()


class IsAuthenticatedAdminOrStaff(BasePermission):
    """
    Allows access only to:
    - Authenticated users who are staff, admin (superuser), or both.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser or
             (request.user.is_staff and request.user.is_superuser))
        )


class UserMinimalSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'full_name')
        read_only_fields = fields

    def get_full_name(self, obj):
        return obj.get_full_name()


class CustomerProfileMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerProfile
        fields = ('id', 'role', 'company_name')
        read_only_fields = fields


class StaffProfileMinimalSerializer(serializers.ModelSerializer):

    class Meta:
        model = StaffProfile
        fields = ('id', 'role', 'specializations')
        read_only_fields = fields
