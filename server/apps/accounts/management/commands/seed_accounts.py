# apps/accounts/management/commands/seed_accounts.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django_seed import Seed
from faker import Faker
from firebase_admin import auth as firebase_auth

from apps.accounts.models import User, CustomerProfile, StaffProfile
from utils.constants import UserRoles, ContactMethods
from utils.firebase_conn import firebase_conn

# Initialize Faker, Seeder and Firebase
faker = Faker()
seeder = Seed.seeder()
firebase_conn()  # Initialize Firebase connection


class Command(BaseCommand):
    help = 'Seed the database with customer and staff accounts with Firebase integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clients',
            default=10,
            type=int,
            help='Number of individual clients to create'
        )
        parser.add_argument(
            '--companies',
            default=15,
            type=int,
            help='Number of company clients to create'
        )
        parser.add_argument(
            '--staff',
            default=5,
            type=int,
            help='Number of staff members to create'
        )

    def generate_phone(self):
        """Generate a valid phone number format"""
        return f"+254{faker.msisdn()[4:]}"  # Generate Kenyan phone numbers

    def generate_availability(self):
        """Generate a realistic weekly availability schedule"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        availability = {}

        for day in days:
            # Most staff work standard hours
            if faker.random.random() < 0.8:  # 80% chance of standard hours
                availability[day] = {
                    'start': '08:00',
                    'end': '18:00'
                }
            else:  # 20% chance of different hours
                start_hour = faker.random_int(7, 10)
                end_hour = faker.random_int(16, 19)
                availability[day] = {
                    'start': f'{start_hour:02d}:00',
                    'end': f'{end_hour:02d}:00'
                }

        return availability

    def generate_specializations(self):
        """Generate a list of technical specializations"""
        specializations_list = [
            'Hardware Repair',
            'Software Troubleshooting',
            'Data Recovery',
            'Network Configuration',
            'Mobile Device Repair',
            'Laptop Repair',
            'Screen Replacement',
            'Battery Replacement',
            'Operating System Installation',
            'Virus Removal'
        ]
        return faker.random_choices(
            specializations_list,
            length=faker.random_int(2, 4)
        )

    def create_firebase_user(self, email, password, display_name):
        """Create a Firebase user and return the UID"""
        try:
            firebase_user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=display_name,
                email_verified=False
            )
            return firebase_user.uid
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create Firebase user for {email}: {str(e)}"))
            return None

    def cleanup_firebase_user(self, uid):
        """Clean up Firebase user in case of failure"""
        if uid:
            try:
                firebase_auth.delete_user(uid)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Failed to delete Firebase user {uid}: {str(e)}"))

    def clear_all_firebase_users(self):
        """Clear all users from Firebase"""
        try:
            # Get all Firebase users in batches
            page = firebase_auth.list_users()
            deleted_count = 0

            while page:
                for user in page.users:
                    try:
                        firebase_auth.delete_user(user.uid)
                        deleted_count += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f"Failed to delete Firebase user {user.uid}: {str(e)}"
                        ))

                # Get next batch of users
                if page.has_next_page:
                    page = firebase_auth.list_users(page_token=page.next_page_token)
                else:
                    break

            self.stdout.write(self.style.SUCCESS(
                f"Successfully deleted {deleted_count} Firebase users"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Error clearing Firebase users: {str(e)}"
            ))

    @transaction.atomic
    def create_user(self, is_staff=False, is_company=False):
        """Create a base user with appropriate attributes and Firebase account"""
        email = faker.company_email() if is_company else faker.email()
        first_name = faker.company() if is_company else faker.first_name()
        last_name = "" if is_company else faker.last_name()
        password = 'password#123'

        # Create Firebase user first
        display_name = first_name if is_company else f"{first_name} {last_name}"
        firebase_uid = self.create_firebase_user(email, password, display_name)

        if not firebase_uid:
            raise Exception(f"Failed to create Firebase user for {email}")

        try:
            user = User.objects.create(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone_number=self.generate_phone(),
                is_staff=is_staff,
                email_verified=True,
                phone_verified=True,
                firebase_uid=firebase_uid
            )
            user.set_password(password)
            user.save()

            return user
        except Exception as e:
            # If Django user creation fails, clean up the Firebase user
            self.cleanup_firebase_user(firebase_uid)
            raise e

    @transaction.atomic
    def create_client(self, is_company=False):
        """Create a client (individual or company) with associated profile"""
        try:
            user = self.create_user(is_company=is_company)

            profile_data = {
                'user': user,
                'role': UserRoles.COMPANY if is_company else UserRoles.CLIENT,
                'preferred_contact': faker.random_element(ContactMethods.CHOICES)[0],
                'address': faker.address(),
                'notes': faker.text(max_nb_chars=200)
            }

            if is_company:
                profile_data['company_name'] = user.first_name

            CustomerProfile.objects.create(**profile_data)
            return user
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create client: {str(e)}"))
            raise e

    @transaction.atomic
    def create_staff_member(self):
        """Create a staff member with associated profile"""
        try:
            user = self.create_user(is_staff=True)

            StaffProfile.objects.create(
                user=user,
                role=faker.random_element([
                    UserRoles.TECHNICIAN,
                    UserRoles.ADMIN,
                    UserRoles.RECEPTIONIST
                ]),
                specializations=self.generate_specializations(),
                availability=self.generate_availability()
            )
            return user
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to create staff member: {str(e)}"))
            raise e

    def create_superuser(self):
        """Create a superuser with Firebase account"""
        email = 'admin@example.com'
        password = 'admin#123'

        # Check if superuser already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write("Superuser already exists, skipping creation.")
            return

        # Create Firebase user for superuser
        firebase_uid = self.create_firebase_user(
            email=email,
            password=password,
            display_name='Admin User'
        )

        if firebase_uid:
            try:
                superuser = User.objects.create_superuser(
                    email=email,
                    password=password,
                    first_name='Admin',
                    last_name='User',
                    firebase_uid=firebase_uid
                )
                self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
                return superuser
            except Exception as e:
                self.cleanup_firebase_user(firebase_uid)
                self.stdout.write(self.style.ERROR(f"Failed to create superuser: {str(e)}"))
                raise e

    def handle(self, *args, **options):
        if input("Do you want to clear existing user data? (yes/no): ").lower() == 'yes':
            self.stdout.write("Clearing existing user data...")

            # Clear Firebase users first
            self.stdout.write("Clearing Firebase users...")
            self.clear_all_firebase_users()

            # Then clear Django users
            self.stdout.write("Clearing Django users...")
            User.objects.all().delete()

            self.stdout.write(self.style.SUCCESS("Successfully cleared all user data"))

        success_count = {'clients': 0, 'companies': 0, 'staff': 0}

        # Create individual clients
        self.stdout.write("Creating individual clients...")
        for i in range(options['clients']):
            try:
                self.create_client()
                success_count['clients'] += 1
                self.stdout.write(f"Created client {i + 1}/{options['clients']}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create client {i + 1}: {str(e)}"))

        # Create company clients
        self.stdout.write("Creating company clients...")
        for i in range(options['companies']):
            try:
                self.create_client(is_company=True)
                success_count['companies'] += 1
                self.stdout.write(f"Created company {i + 1}/{options['companies']}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create company {i + 1}: {str(e)}"))

        # Create staff members
        self.stdout.write("Creating staff members...")
        for i in range(options['staff']):
            try:
                self.create_staff_member()
                success_count['staff'] += 1
                self.stdout.write(f"Created staff member {i + 1}/{options['staff']}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to create staff member {i + 1}: {str(e)}"))

        # Create superuser
        self.stdout.write("Creating superuser...")
        self.create_superuser()

        self.stdout.write(self.style.SUCCESS(f"""
\nSuccessfully created:
- {success_count['clients']}/{options['clients']} individual clients
- {success_count['companies']}/{options['companies']} company clients
- {success_count['staff']}/{options['staff']} staff members
- 1 superuser (admin@example.com / admin#123)

All accounts created with password: password#123
"""))
