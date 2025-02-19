import logging
from datetime import timedelta

from django.contrib.auth import get_user_model, login
from django.db import transaction
from django.middleware.csrf import get_token
from django.utils import timezone
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from utils.firebase_conn import firebase_conn
from .models import StaffProfile
from .serializers import (
    RegisterSerializer, CustomerProfileSerializer, StaffProfileSerializer, PasswordChangeSerializer,
    UserSerializer, UserUpdateSerializer, AdminDashboardSerializer,
    StaffDashboardSerializer, CustomerDashboardSerializer
)

User = get_user_model()
firebase_conn()
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    """
    View for user registration with automatic profile creation.
    Uses Customer/StaffProfileSerializer for validation and atomic transactions.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        with transaction.atomic():
            user = serializer.save()
            profile_type = self.request.data.get('profile_type', 'customer').lower()

            # 2. Validate profile type
            if profile_type not in ['customer', 'staff']:
                raise serializers.ValidationError(
                    {'profile_type': 'Must be "customer" or "staff".'}
                )
            # 3. Prepare profile data
            profile_data = self.request.data.copy()
            profile_data['user_email'] = user.email  # Link to the new user needed by the customer and staff serializers

            # 4. Staff-specific logic
            if profile_type == 'staff':
                user.is_staff = True
                user.save(update_fields=['is_staff'])

            # 5. Use profile serializer to validate and create the profile
            profile_serializer_class = CustomerProfileSerializer if profile_type == 'customer' else StaffProfileSerializer
            profile_serializer = profile_serializer_class(data=profile_data, context=self.get_serializer_context())

            if not profile_serializer.is_valid():
                # Log profile validation errors
                print("Profile validation errors:", profile_serializer.errors)
                raise serializers.ValidationError(profile_serializer.errors)
            profile_serializer.save()

            response_data = {
                'message': f'Successfully created {profile_type} account',
                'data': {
                    'login_token': user.customer_profile.login_token if profile_type == 'customer' else user.staff_profile.login_token,
                    'email': user.email,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        return super().get_permissions()

    def get_admin_data(self, request):
        user = request.user
        if not user.is_superuser:
            return Response(
                {'error': 'You do not have permission to access this endpoint.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Prepare context data
        context_data = {
            'active_staff': StaffProfile.objects.filter(user__is_active=True).count()
        }

        return AdminDashboardSerializer(context_data).data

    def get_staff_data(self, request):
        data = {
            'assigned_repairs': 0,
            'pending_repairs': 0,
            'completed_repairs': 0
        }
        return StaffDashboardSerializer(data).data

    def get_customer_data(self, request):
        data = {
            'total_bookings': 0,
            'active_bookings': 0,
            'completed_bookings': 0
        }
        return CustomerDashboardSerializer(data).data

    @action(detail=False, methods=['GET'])
    def me(self, request):
        user = request.user
        logger.info(f"\n=== Processing /me request for {user.email} ===")

        response_data = {
            'user': UserSerializer(user, context={'request': request}).data,
            'role': self._determine_user_role(user)
        }

        if user.is_superuser:
            logger.info("Getting admin dashboard data")
            response_data['dashboard'] = self.get_admin_data(request)
        elif user.is_staff:
            logger.info("Getting staff dashboard data")
            response_data['dashboard'] = self.get_staff_data(request)
        else:
            logger.info("Getting customer dashboard data")
            response_data['dashboard'] = self.get_customer_data(request)

        logger.info(f"Returning data for {user.email}")
        return Response(response_data)

    def _determine_user_role(self, user):
        """Helper method to determine user role"""
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'staff'
        return 'customer'

    @action(detail=True, methods=['POST'])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = PasswordChangeSerializer(data=request.data)

        if serializer.is_valid():
            if not user.check_password(serializer.data.get('old_password')):
                return Response({'error': 'Wrong password.'},
                                status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data.get('new_password'))
            user.save()
            return Response({'status': 'password changed'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Then our main admin session view
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def admin_session(request):
    """
    Handles both initial session setup (GET) and session creation (POST)
    """
    if request.method == 'GET':
        # Set both CSRF and session cookies on GET
        if not request.session.session_key:
            request.session.create()

        # Explicitly get CSRF token to ensure it's set
        csrf_token = get_token(request)

        response = Response({
            "message": "Session initialized",
            "csrf_token": csrf_token
        })

        # Set session cookie explicitly
        response.set_cookie(
            'sessionid',
            request.session.session_key,
            domain='127.0.0.1',
            max_age=86400,
            secure=False,  # Set to True in production
            httponly=True,
            samesite='Lax'
        )

        return response

    elif request.method == 'POST':
        # Handle admin session creation
        user = request.user

        if not (user.is_staff or user.is_superuser):
            return Response(
                {"error": "Admin privileges required"},
                status=status.HTTP_403_FORBIDDEN
            )

        login(request, user)

        # Create new session for admin access
        request.session.cycle_key()
        request.session.set_expiry(86400)

        response = Response({
            "message": "Admin session created successfully",
            "admin_url": "/admin/"
        })

        return response
