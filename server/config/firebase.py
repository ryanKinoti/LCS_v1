import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import resolve
from django.utils.functional import SimpleLazyObject
from firebase_admin import auth
from rest_framework.exceptions import AuthenticationFailed

from config import settings
from utils.firebase_conn import firebase_conn

User = get_user_model()
firebase_conn()
logger = logging.getLogger(__name__)


class FirebaseAuthenticationMiddleware:
    """
    Middleware that authenticates users using Firebase tokens.

    This middleware intercepts requests, verifies Firebase ID tokens,
    and attaches authenticated user instances to the request.
    It handles loading user profiles and role information efficiently.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        Main middleware method that processes each request.
        Uses SimpleLazyObject to defer user loading until needed.
        """
        resolved = resolve(request.path)
        if resolved.app_name == 'admin' or request.path.startswith('/admin/'):
            return self.get_response(request)

        if any(request.path.startswith(exempt_url) for exempt_url in getattr(settings, 'FIREBASE_MIDDLEWARE_EXEMPT_URLS', [])):
            return self.get_response(request)

        request.user = SimpleLazyObject(lambda: self._get_user(request))
        return self.get_response(request)

    def _get_token_from_header(self, request):
        auth_header = request.headers.get('Authorization', '')
        logger.info(f"Auth header received: {auth_header[:20]}..." if auth_header else "No auth header")

        if not auth_header.startswith('Bearer '):
            return None

        return auth_header.split(' ')[1]

    def _get_user(self, request):
        """
        Core authentication method that verifies tokens and loads user data.
        Returns authenticated user or raises AuthenticationFailed.
        """
        logger.info("\n=== Firebase Authentication Process ===")

        if hasattr(request, '_cached_user') and request._cached_user.is_authenticated:
            return request._cached_user

        try:
            token = self._get_token_from_header(request)
            if not token:
                logger.warning("No token found - returning anonymous user")
                return AnonymousUser()

            try:
                logger.info("Verifying Firebase token...")

                decoded_token = auth.verify_id_token(token, clock_skew_seconds=30)
                firebase_uid = decoded_token.get('uid')

                logger.info(f"Token verified for Firebase UID: {firebase_uid[:10]}...")
            except auth.InvalidIdTokenError as e:
                raise AuthenticationFailed('Invalid token')

            try:
                user = User.objects.select_related(
                    'customer_profile',
                    'staff_profile'
                ).get(firebase_uid=firebase_uid)
                logger.info(f"Found user: {user.email}")
            except User.DoesNotExist:

                logger.error(f"No user found for Firebase UID: {firebase_uid}")

                raise AuthenticationFailed('User not found')

            if hasattr(user, 'customer_profile'):
                user.profile_type = 'customer'
                user.profile = user.customer_profile
                logger.info("Attached customer profile")
            elif hasattr(user, 'staff_profile'):
                user.profile_type = 'staff'
                user.profile = user.staff_profile
                logger.info("Attached staff profile")

            logger.info("Authentication successful")
            return user

        except AuthenticationFailed:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            raise AuthenticationFailed(str(e))
