from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from firebase_admin import auth as firebase_auth
from django.db import transaction

from utils.firebase_conn import firebase_conn

User = get_user_model()
firebase_conn()


class Command(BaseCommand):
    help = "Create a Django superuser and corresponding Firebase user"

    def add_arguments(self, parser):
        parser.add_argument('--email', help="User's email address")
        parser.add_argument('--password', help="User's password")
        parser.add_argument('--first_name', help="User's first name")
        parser.add_argument('--last_name', help="User's last name")

    def validate_input(self, email, password, first_name, last_name):
        """Validate input parameters
        :rtype: validated input parameters
        """
        try:
            validate_email(email)
        except ValidationError:
            raise CommandError("Invalid email format")

        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters long")

        if not first_name or not last_name:
            raise CommandError("First name and last name are required")

    def handle(self, *args, **options):
        email = options['email'] or input("Email: ")
        password = options['password'] or input("Password: ")
        first_name = options['first_name'] or input("First Name: ")
        last_name = options['last_name'] or input("Last Name: ")

        # Validate inputs
        self.validate_input(email, password, first_name, last_name)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f"User with email {email} already exists")

        try:
            # Use transaction to ensure both operations succeed or fail together
            with transaction.atomic():
                # Create Firebase user first
                try:
                    firebase_user = firebase_auth.create_user(
                        email=email,
                        password=password,
                        email_verified=True,
                        display_name=f"{first_name} {last_name}"
                    )
                except Exception as e:
                    raise CommandError(f"Firebase user creation failed: {str(e)}")

                try:
                    # Create Django superuser
                    user = User.objects.create_superuser(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        firebase_uid=firebase_user.uid,  # Store Firebase UID
                        email_verified=True  # Since it's a superuser
                    )
                except Exception as e:
                    # If Django user creation fails, clean up Firebase user
                    firebase_auth.delete_user(firebase_user.uid)
                    raise CommandError(f"Django user creation failed: {str(e)}")

                # Set custom claims in Firebase
                try:
                    firebase_auth.set_custom_user_claims(
                        firebase_user.uid,
                        {
                            'is_superuser': True,
                            'is_staff': True,
                            'django_id': str(user.id)  # Include Django user ID in claims
                        }
                    )
                except Exception as e:
                    # If setting claims fails, clean up both users
                    user.delete()
                    firebase_auth.delete_user(firebase_user.uid)
                    raise CommandError(f"Setting Firebase claims failed: {str(e)}")

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully created superuser:\n'
                    f'Email: {email}\n'
                    f'Name: {first_name} {last_name}\n'
                    f'Firebase UID: {firebase_user.uid}'
                )
            )

        except CommandError as e:
            self.stdout.write(self.style.ERROR(str(e)))
            raise

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error creating superuser: {str(e)}')
            )
            raise
