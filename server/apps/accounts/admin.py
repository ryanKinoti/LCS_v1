from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomerProfile, StaffProfile, User


class CustomerProfileInline(admin.StackedInline):
    model = CustomerProfile
    can_delete = False
    fk_name = "user"


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    fk_name = "user"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('firebase_uid', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'email_verified',
                    'phone_verified')
    list_filter = ('is_staff', 'is_superuser', 'email_verified', 'phone_verified', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Verification'), {'fields': ('email_verified', 'phone_verified')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    inlines = [CustomerProfileInline, StaffProfileInline]


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user_email', 'role', 'company_name', 'preferred_contact', 'created_at')
    list_filter = ('role', 'preferred_contact', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'company_name', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role', 'preferred_contact')
        }),
        ('Company Details', {
            'fields': ('company_name', 'address')
        }),
        ('Additional Information', {
            'fields': ('notes', 'login_token'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'user_email', 'role', 'get_specializations', 'is_available', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'specializations', 'role')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'role')
        }),
        ('Technical Details', {
            'fields': ('specializations', 'availability'),
            'description': 'Technical expertise and schedule information'
        }),
        ('Security', {
            'fields': ('login_token',),
            'classes': ('collapse',),
            'description': 'Authentication related information'
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    get_full_name.short_description = 'Full Name'

    def user_email(self, obj):
        return obj.user.email

    user_email.short_description = 'Email'

    def get_specializations(self, obj):
        return obj.specializations

    get_specializations.short_description = 'Specializations'

    def is_available(self, obj):
        return bool(obj.availability)

    is_available.boolean = True
    is_available.short_description = 'Has Schedule'
