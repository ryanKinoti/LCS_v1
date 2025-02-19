# apps/accounts/models.py
import secrets

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from utils.constants import UserRoles, ContactMethods

phone_validator = RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.

    This manager handles all user creation operations including:
    - Regular user creation with email authentication
    - Superuser creation with administrative privileges

    Inheritance:
        BaseUserManager: Provides base functionality for managing user creation

    Usage:
        Used as the objects manager for the User model through:
        objects = CustomUserManager()
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    firebase_uid = models.CharField(max_length=128, blank=True, null=True, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150, null=True)
    last_name = models.CharField(_('last name'), max_length=150, null=True)
    phone_number = models.CharField(max_length=16, validators=[phone_validator], blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} <{self.email}>"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    role = models.CharField(max_length=20, choices=UserRoles.CUSTOMER_ROLES, null=True)
    preferred_contact = models.CharField(max_length=10, choices=ContactMethods.CHOICES, default='email')
    company_name = models.CharField(max_length=255, blank=True, null=True)
    login_token = models.CharField(max_length=128, blank=True, null=True, default=secrets.token_urlsafe)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer Profile - {self.user.email} ({self.role})"

    class Meta:
        verbose_name = _("Customer Profile")
        verbose_name_plural = _("Customer Profiles")


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    role = models.CharField(max_length=20, choices=UserRoles.STAFF_ROLES)
    specializations = models.JSONField(default=list, help_text=_('List of technical specializations'))
    availability = models.JSONField(
        default=dict,
        help_text=_('Weekly availability schedule. Indicate the Start and End timings accurately.')
    )
    login_token = models.CharField(max_length=128, blank=True, null=True, default=secrets.token_urlsafe)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Staff Profile - {self.user.email} ({self.role})"

    class Meta:
        verbose_name = _("Staff Profile")
        verbose_name_plural = _("Staff Profiles")
