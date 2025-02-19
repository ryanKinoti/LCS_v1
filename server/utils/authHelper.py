from typing import Optional, Dict, Any

from django.contrib.auth import get_user_model
from firebase_admin import auth

User = get_user_model()

def verify_firebase_superuser(token: str) -> bool:
    """
    Verifies if a Firebase token belongs to a superuser by checking custom claims.

    This function is particularly useful when you need to verify superuser status
    during API calls or authentication processes.

    Args:
        token (str): The Firebase ID token to verify

    Returns:
        bool: True if the token belongs to a superuser, False otherwise

    Example:
        token = request.headers.get('Authorization').split('Bearer ').pop()
        is_superuser = verify_firebase_superuser(token)
        if is_superuser:
            # Allow superuser-specific actions
    """
    try:
        # Verify and decode the token
        decoded_token = auth.verify_id_token(token)

        # Extract custom claims - these were set during superuser creation
        custom_claims = decoded_token.get('claims', {})

        # Check if all required superuser claims are present and true
        return bool(
            custom_claims.get('is_superuser') and
            custom_claims.get('is_staff') and
            custom_claims.get('django_id')  # Ensures the user exists in Django
        )
    except Exception as e:
        # Log the error if needed
        print(f"Error verifying superuser token: {str(e)}")
        return False

def sync_user_privileges(user: User) -> None:
    """
    Synchronizes a Django user's privileges with their Firebase custom claims.

    This function should be called whenever a user's privileges are modified in Django
    to ensure Firebase stays in sync.

    Args:
        user (User): The Django user instance whose privileges need to be synced

    Raises:
        ValueError: If the user doesn't have a Firebase UID

    Example:
        user.is_staff = True
        user.save()
        sync_user_privileges(user)  # Sync the new staff status to Firebase
    """
    if not user.firebase_uid:
        raise ValueError(f"User {user.email} does not have a Firebase UID")

    try:
        # Get current Firebase user record
        user_record = auth.get_user(user.firebase_uid)
        current_claims = user_record.custom_claims or {}

        # Prepare new claims
        new_claims = {
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'django_id': str(user.id),
            'email_verified': user.email_verified
        }

        # Only update if claims have changed to avoid unnecessary Firebase calls
        if current_claims != new_claims:
            auth.set_custom_user_claims(user.firebase_uid, new_claims)

    except auth.UserNotFoundError:
        raise ValueError(f"User {user.email} not found in Firebase")
    except Exception as e:
        raise ValueError(f"Failed to sync privileges: {str(e)}")

def get_or_create_firebase_user(user: User, password: Optional[str] = None) -> Dict[str, Any]:
    """
    Gets an existing Firebase user or creates a new one for a Django user.

    This function is useful when you need to ensure a Django user has a
    corresponding Firebase account.

    Args:
        user (User): The Django user instance
        password (str, optional): Password to set for new Firebase users

    Returns:
        dict: Firebase user data including UID and email

    Example:
        firebase_user = get_or_create_firebase_user(django_user, "temp_password")
        print(f"Firebase UID: {firebase_user['uid']}")
    """
    try:
        # Try to get existing Firebase user
        firebase_user = auth.get_user_by_email(user.email)

    except auth.UserNotFoundError:
        # Create new Firebase user if not found
        if not password:
            raise ValueError("Password required for new Firebase user")

        firebase_user = auth.create_user(
            email=user.email,
            password=password,
            display_name=user.get_full_name(),
            email_verified=user.email_verified
        )

        # Store Firebase UID in Django user
        user.firebase_uid = firebase_user.uid
        user.save(update_fields=['firebase_uid'])

        # Sync privileges
        sync_user_privileges(user)

    return {
        'uid': firebase_user.uid,
        'email': firebase_user.email,
        'display_name': firebase_user.display_name,
        'email_verified': firebase_user.email_verified
    }