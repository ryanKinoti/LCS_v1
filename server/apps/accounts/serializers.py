from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission
from firebase_admin import auth as firebase_auth

from .models import CustomerProfile, StaffProfile

User = get_user_model()


# UAC serializers
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


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    - **Serialize User Instances**: Converts User model instances into JSON format.
    - **Deserialize Data**: Converts JSON data back into User model instances.
    - **Read-Only Fields**: Ensures that certain fields are read-only and cannot be modified through the serializer.
    - **Custom Field**: The full_name field is a custom field that is populated using the get_full_name method.

    Attributes:
        full_name (serializers.SerializerMethodField): Custom field to get the full name of the user.
    """
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'phone_number')
        read_only_fields = ('id', 'email_verified', 'phone_verified', 'is_active', 'is_staff', 'is_superuser')

    def get_full_name(self, obj):
        return obj.get_full_name()


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = CustomerProfile
        fields = ('user', 'user_email', 'role', 'preferred_contact', 'company_name', 'address', 'login_token',
                  'notes', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'login_token')

    def validate_user_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        self.context['user_instance'] = user
        return value

    def create(self, validated_data):
        user_email = validated_data.pop('user_email', None)
        if user_email:
            validated_data['user'] = self.context.get('user_instance')
        return super().create(validated_data)


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = StaffProfile
        fields = ('user', 'user_email', 'login_token', 'role',
                  'specializations', 'availability', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'login_token')

    def validate_user_email(self, value):
        try:
            user = User.objects.get(email=value)
            self.context['user_instance'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value

    def validate_specializations(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Specializations must be a list")
        return value

    def validate_availability(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Availability must be a dictionary")
        return value

    def create(self, validated_data):
        user_email = validated_data.pop('user_email', None)
        if user_email:
            validated_data['user'] = self.context.get('user_instance')
        return super().create(validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, min_length=8)
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password', 'confirm_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                "Password cannot be entirely numeric."
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        try:
            firebase_user = firebase_auth.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                display_name=f"{validated_data['first_name']} {validated_data['last_name']}",
                email_verified=False,
            )
            validated_data.pop('confirm_password')
            password = validated_data.pop('password')
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.firebase_uid = firebase_user.uid
            user.save()

            return user
        except Exception as e:
            try:
                firebase_auth.delete_user(firebase_user.uid)
            except Exception:
                pass
            raise serializers.ValidationError({'firebase_error': str(e)})


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, min_length=8)
    new_password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'}, min_length=8)

    def validate_old_password(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError("New password must be different from old password.")
        return data


# Dashboard serializers
class AdminDashboardSerializer(serializers.Serializer):
    """
    Serializer for admin dashboard overview data.
    Structures the statistics and metrics for admin view.
    """
    total_repairs = serializers.IntegerField()
    pending_repairs = serializers.IntegerField()
    low_stock_items = serializers.IntegerField()
    total_inventory_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_staff = serializers.IntegerField()
    revenue_data = serializers.DictField()
    recent_activity = serializers.ListField()


class StaffDashboardSerializer(serializers.Serializer):
    assigned_repairs = serializers.IntegerField()
    pending_repairs = serializers.IntegerField()
    completed_repairs = serializers.IntegerField()


class CustomerDashboardSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    active_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
