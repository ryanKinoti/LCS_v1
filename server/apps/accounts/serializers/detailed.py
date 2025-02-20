# apps/accounts/serializers/detailed.py
from datetime import datetime

from django.contrib.auth import get_user_model
from firebase_admin import auth as firebase_auth
from rest_framework import serializers

from apps.accounts.models import StaffProfile, CustomerProfile
from apps.accounts.serializers import CustomerProfileMinimalSerializer, StaffProfileMinimalSerializer
from utils.constants import BUSINESS_HOURS, UserRoles

User = get_user_model()


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
    profile_type = serializers.SerializerMethodField()
    customer_profile = serializers.SerializerMethodField()
    staff_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'full_name', 'phone_number', 'email_verified',
                  'phone_verified', 'profile_type', 'customer_profile', 'staff_profile',)
        read_only_fields = ('id', 'email', 'email_verified', 'phone_verified', 'profile_type', 'is_active', 'is_staff',
                            'is_superuser')

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_profile_type(self, obj):
        if hasattr(obj, 'customer_profile'):
            return 'customer'
        elif hasattr(obj, 'staff_profile'):
            return 'staff'
        return None

    def get_customer_profile(self, obj):
        if hasattr(obj, 'customer_profile'):
            return CustomerProfileMinimalSerializer(obj.customer_profile).data
        return None

    def get_staff_profile(self, obj):
        if hasattr(obj, 'staff_profile'):
            return StaffProfileMinimalSerializer(obj.staff_profile).data
        return None

    def validate_phone_number(self, value):
        if value:
            # Remove any spaces or special characters
            value = ''.join(filter(str.isdigit, value))
            if not value.startswith('+'):
                value = '+' + value
        return value


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = CustomerProfile
        fields = ('user', 'user_email', 'role', 'preferred_contact', 'company_name', 'address', 'login_token',
                  'notes', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at', 'login_token')

    def validate(self, data):
        if data.get('role') == UserRoles.COMPANY:
            if not data.get('company_name'):
                raise serializers.ValidationError({
                    'company_name': "Company name is required for company accounts."
                })
        user_email = data.get('user_email')
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                if hasattr(user, 'customer_profile'):
                    raise serializers.ValidationError({
                        'user_email': "This user already has a customer profile."
                    })
                data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'user_email': "No user found with this email."
                })
        return data

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
        if not value:
            raise serializers.ValidationError("At least one specialization is required")
        return value

    def validate_availability(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Availability must be a dictionary")

        valid_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        business_start = BUSINESS_HOURS['start_time']
        business_end = BUSINESS_HOURS['end_time']

        for day, schedule in value.items():
            if day.lower() not in valid_days:
                raise serializers.ValidationError(f"Invalid day: {day}")

            if 'start' not in schedule or 'end' not in schedule:
                raise serializers.ValidationError(f"Missing start/end time for {day}")

            if not isinstance(schedule, dict) or 'start' not in schedule or 'end' not in schedule:
                raise serializers.ValidationError(f"Invalid schedule format for {day}")

            try:
                start_time = datetime.strptime(schedule['start'], '%H:%M').time()
                end_time = datetime.strptime(schedule['end'], '%H:%M').time()
                business_start_time = datetime.strptime(business_start, '%I:%M %p').time()
                business_end_time = datetime.strptime(business_end, '%I:%M %p').time()

                if start_time >= end_time:
                    raise serializers.ValidationError(f"End time must be after start time for {day}")

                if start_time < business_start_time or end_time > business_end_time:
                    raise serializers.ValidationError(
                        f"Schedule for {day} must be within business hours ({business_start} - {business_end})"
                    )

            except ValueError:
                raise serializers.ValidationError(f"Invalid time format for {day}. Use HH:MM format")
        return value

    def validate(self, data):
        user_email = data.get('user_email')
        if user_email:
            try:
                user = User.objects.get(email=user_email)
                if hasattr(user, 'staff_profile'):
                    raise serializers.ValidationError({
                        'user_email': "This user already has a staff profile."
                    })
                data['user'] = user
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'user_email': "No user found with this email."
                })

        return data

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
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'password', 'confirm_password', 'profile_type')

    def validate_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError(
                "Password cannot be entirely numeric."
            )
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        password = data['password']
        if len(password) < 8:
            raise serializers.ValidationError({
                'password': "Password must be at least 8 characters long."
            })
        if password.isdigit():
            raise serializers.ValidationError({
                'password': "Password cannot be entirely numeric."
            })
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({
                'password': "Password must contain at least one number."
            })
        return data

    def create(self, validated_data):
        try:
            firebase_user = firebase_auth.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                display_name=f"{validated_data['first_name']} {validated_data['last_name']}",
                phone_number=validated_data.get('phone_number'),
                email_verified=False,
            )
            validated_data.pop('confirm_password')
            profile_type = validated_data.pop('profile_type')
            password = validated_data.pop('password')
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.firebase_uid = firebase_user.uid
            if profile_type == 'staff':
                user.is_staff = True
            user.save()

            return user
        except Exception as e:
            if 'firebase_user' in locals():
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
        password = data['new_password']
        if password.isdigit():
            raise serializers.ValidationError({
                'new_password': "Password cannot be entirely numeric."
            })
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({
                'new_password': "Password must contain at least one number."
            })
        return data
