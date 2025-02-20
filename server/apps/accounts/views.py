import logging
from logging import exception

from django.contrib.auth import get_user_model, login
from django.db import transaction
from django.middleware.csrf import get_token
from rest_framework import generics, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from utils.firebase_conn import firebase_conn
from .models import StaffProfile
from .permissions import IsAdminUser
from .serializers import (
    RegisterSerializer, CustomerProfileSerializer, StaffProfileSerializer, PasswordChangeSerializer,
    UserSerializer, UserUpdateSerializer, AdminDashboardSerializer,
    StaffDashboardSerializer, CustomerDashboardSerializer, UserMinimalSerializer
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

    @transaction.atomic
    def perform_create(self, serializer):
        logger.info("Starting user registration process")
        try:
            user = serializer.save()
            profile_type = self.request.data.get('profile_type', 'customer').lower()

            # 2. Validate profile type
            if profile_type not in ['customer', 'staff']:
                raise serializers.ValidationError(
                    {'profile_type': 'Must be "customer" or "staff".'}
                )
            # 3. Prepare profile data
            profile_data = self.request.data.copy()
            profile_data['user_email'] = user.email

            # 4. Staff-specific logic
            if profile_type == 'staff':
                user.is_staff = True
                user.save(update_fields=['is_staff'])

            # 5. Use profile serializer to validate and create the profile
            if profile_type == 'customer':
                profile_serializer = CustomerProfileSerializer(
                    data=profile_data,
                    context=self.get_serializer_context()
                )
            elif profile_type == 'staff':
                profile_serializer = StaffProfileSerializer(
                    data=profile_data,
                    context=self.get_serializer_context()
                )
            else:
                raise ValidationError({"profile_type": "Invalid profile type"})

            if profile_serializer.is_valid():
                profile = profile_serializer.save(user=user)
                logger.info(f"Successfully created {profile_type} profile for {user.email}")

                return Response({
                    'message': f'Successfully created {profile_type} account',
                    'data': {
                        'email': user.email,
                        'profile_type': profile_type,
                        'login_token': profile.login_token
                    }
                }, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Profile validation failed: {profile_serializer.errors}")
                raise ValidationError(profile_serializer.errors)
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise ValidationError(str(e))


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on user role:

        - Superusers can see all users
        - Staff can see customers
        - Customers can only see themselves
        """
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        elif user.is_staff:
            return User.objects.filter(customer_profile__isnull=False)
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserMinimalSerializer

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

    def _determine_user_role(self, user):
        if user.is_superuser:
            return 'admin'
        elif user.is_staff:
            return 'staff'
        return 'customer'

    @action(detail=False, methods=['GET'])
    def me(self, request):
        user = request.user
        logger.info(f"\n=== Processing /me request for {user.email} ===")
        try:
            context = {'request': request}
            if request.query_params.get('detail') == 'full':
                serializer_class = UserSerializer
            else:
                serializer_class = UserMinimalSerializer
            response_data = {
                'user': serializer_class(user, context=context).data,
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
        except Exception as e:
            logger.error(f"Error fetching dashboard data: {str(e)}")
            return Response(
                {'error': 'Failed to fetch dashboard data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'status': 'success', 'is_active': user.is_active})

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
