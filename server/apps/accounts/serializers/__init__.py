# apps/accounts/serializers/__init__.py
from .base import (
    UserMinimalSerializer,
    CustomerProfileMinimalSerializer,
    StaffProfileMinimalSerializer
)
from .detailed import (
    UserSerializer,
    CustomerProfileSerializer,
    StaffProfileSerializer,
    RegisterSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer
)
from .dashboard import (
    AdminDashboardSerializer,
    StaffDashboardSerializer,
    CustomerDashboardSerializer
)

__all__ = [
    # Base serializers
    'UserMinimalSerializer',
    'CustomerProfileMinimalSerializer',
    'StaffProfileMinimalSerializer',

    # Detailed serializers
    'UserSerializer',
    'CustomerProfileSerializer',
    'StaffProfileSerializer',
    'RegisterSerializer',
    'UserUpdateSerializer',
    'PasswordChangeSerializer',

    # Dashboard serializers
    'AdminDashboardSerializer',
    'StaffDashboardSerializer',
    'CustomerDashboardSerializer'
]
