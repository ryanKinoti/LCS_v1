# apps/services/management/commands/seed_services.py
import json
import os
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.services.models import ServiceCategory, Service, DetailedService
from config import settings


class Command(BaseCommand):
    help = 'Seed the database with services data from JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            default=os.path.join(
                settings.BASE_DIR,
                'apps',
                'services',
                'management',
                'commands',
                'data.json'
            ),
            help='Path to the JSON file containing services data'
        )

    def validate_json_data(self, data):
        """Validate the structure and content of JSON data"""
        if not isinstance(data, dict) or 'service_categories' not in data:
            raise ValidationError("JSON must contain 'service_categories' key")

        for category in data['service_categories']:
            if not all(k in category for k in ['name', 'description', 'services']):
                raise ValidationError("Each category must have name, description, and services")

            for service in category['services']:
                if not all(k in service for k in ['name', 'description', 'estimated_time', 'details']):
                    raise ValidationError("Each service must have name, description, estimated_time, and details")

                for detail in service['details']:
                    if not all(k in detail for k in ['device', 'price', 'changes']):
                        raise ValidationError("Each detail must have device, price, and changes")

    def parse_time(self, time_str):
        """Parse time string to timedelta"""
        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            return timedelta(hours=hours, minutes=minutes, seconds=seconds)
        except ValueError:
            raise ValidationError(f"Invalid time format: {time_str}. Expected format: HH:MM:SS")

    def handle(self, *args, **options):
        json_file = options['json_file']

        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f"JSON file not found: {json_file}"))
            return

        try:
            with open(json_file, 'r') as f:
                data = json.load(f)

            # Validate JSON structure
            self.validate_json_data(data)

            with transaction.atomic():
                categories_created = 0
                services_created = 0
                details_created = 0

                # Delete existing data if any
                if ServiceCategory.objects.exists():
                    confirm = input("Existing services found. Delete all? (yes/no): ")
                    if confirm.lower() == 'yes':
                        ServiceCategory.objects.all().delete()
                        self.stdout.write("Deleted existing services data")

                # Create new data
                for category_data in data['service_categories']:
                    category = ServiceCategory.objects.create(
                        name=category_data['name'],
                        description=category_data['description']
                    )
                    categories_created += 1

                    for service_data in category_data['services']:
                        service = Service.objects.create(
                            name=service_data['name'],
                            category=category,
                            description=service_data['description'],
                            estimated_time=self.parse_time(service_data['estimated_time']),
                            active=True
                        )
                        services_created += 1

                        for detail_data in service_data['details']:
                            DetailedService.objects.create(
                                service=service,
                                device=detail_data['device'],
                                changes_to_make=detail_data['changes'],
                                price=detail_data['price'],
                                notes=detail_data.get('notes', '')
                            )
                            details_created += 1

                self.stdout.write(self.style.SUCCESS(f"""
Successfully created:
- {categories_created} service categories
- {services_created} services
- {details_created} detailed services
"""))

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON format: {str(e)}"))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f"Data validation error: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding services: {str(e)}"))
