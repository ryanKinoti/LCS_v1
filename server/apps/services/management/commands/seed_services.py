# apps/services/management/commands/seed_services.py
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from datetime import timedelta

from apps.services.models import ServiceCategory, Service, DetailedService, ServicePartsRequired
from utils.constants import Devices

faker = Faker()


class Command(BaseCommand):
    help = 'Seed the database with realistic service categories and services'

    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            default=5,
            type=int,
            help='Number of service categories to create'
        )

    def handle(self, *args, **options):
        self.stdout.write("Creating service categories and services...")

        # Predefined realistic service data
        service_categories = [
            {
                'name': 'Hardware Repairs',
                'description': 'Physical repairs and component replacements',
                'services': [
                    {
                        'name': 'Screen Replacement',
                        'description': 'Replace damaged or faulty display screens',
                        'estimated_time': timedelta(hours=1, minutes=30),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 15000,
                                'changes': 'Replace laptop screen with new compatible model'
                            },
                            {
                                'device': Devices.DESKTOP,
                                'price': 20000,
                                'changes': 'Replace desktop monitor'
                            }
                        ]
                    },
                    {
                        'name': 'Battery Replacement',
                        'description': 'Replace old or faulty batteries',
                        'estimated_time': timedelta(minutes=45),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 8000,
                                'changes': 'Replace laptop battery with new compatible model'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Software Services',
                'description': 'Software installation, updates, and troubleshooting',
                'services': [
                    {
                        'name': 'Operating System Installation',
                        'description': 'Fresh installation or upgrade of operating systems',
                        'estimated_time': timedelta(hours=2),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 5000,
                                'changes': 'Install and configure operating system with necessary drivers'
                            },
                            {
                                'device': Devices.DESKTOP,
                                'price': 5000,
                                'changes': 'Install and configure operating system with necessary drivers'
                            }
                        ]
                    },
                    {
                        'name': 'Virus Removal',
                        'description': 'Remove malware and viruses, install protection',
                        'estimated_time': timedelta(hours=1, minutes=30),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 3500,
                                'changes': 'Scan and remove viruses, install antivirus'
                            },
                            {
                                'device': Devices.DESKTOP,
                                'price': 3500,
                                'changes': 'Scan and remove viruses, install antivirus'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Maintenance Services',
                'description': 'Regular maintenance and cleaning services',
                'services': [
                    {
                        'name': 'Deep Cleaning',
                        'description': 'Thorough cleaning of device components',
                        'estimated_time': timedelta(hours=1),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 3000,
                                'changes': 'Deep clean laptop including keyboard and fans'
                            },
                            {
                                'device': Devices.DESKTOP,
                                'price': 3500,
                                'changes': 'Deep clean desktop components and peripherals'
                            },
                            {
                                'device': Devices.PRINTER,
                                'price': 2500,
                                'changes': 'Clean printer components and calibrate'
                            }
                        ]
                    }
                ]
            },
            {
                'name': 'Data Services',
                'description': 'Data recovery and backup solutions',
                'services': [
                    {
                        'name': 'Data Recovery',
                        'description': 'Recover data from damaged or corrupted storage',
                        'estimated_time': timedelta(hours=3),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 7500,
                                'changes': 'Recover data from damaged hard drive'
                            },
                            {
                                'device': Devices.DESKTOP,
                                'price': 7500,
                                'changes': 'Recover data from damaged hard drive'
                            }
                        ]
                    },
                    {
                        'name': 'Data Backup',
                        'description': 'Create backups of important data',
                        'estimated_time': timedelta(hours=1),
                        'details': [
                            {
                                'device': Devices.LAPTOP,
                                'price': 2500,
                                'changes': 'Create comprehensive data backup'
                            },
                            {
                                'device': Devices.DESKTOP,
                                'price': 2500,
                                'changes': 'Create comprehensive data backup'
                            }
                        ]
                    }
                ]
            }
        ]

        try:
            with transaction.atomic():
                for category_data in service_categories:
                    # Create category
                    category = ServiceCategory.objects.create(
                        name=category_data['name'],
                        description=category_data['description']
                    )

                    # Create services for this category
                    for service_data in category_data['services']:
                        service = Service.objects.create(
                            name=service_data['name'],
                            category=category,
                            description=service_data['description'],
                            estimated_time=service_data['estimated_time'],
                            active=True
                        )

                        # Create detailed services
                        for detail_data in service_data['details']:
                            DetailedService.objects.create(
                                service=service,
                                device=detail_data['device'],
                                changes_to_make=detail_data['changes'],
                                price=detail_data['price'],
                                notes=f"Standard {service_data['name']} for {detail_data['device']}"
                            )

                self.stdout.write(self.style.SUCCESS(f"""
Successfully created:
- {len(service_categories)} service categories
- {sum(len(cat['services']) for cat in service_categories)} services
- {sum(sum(len(service['details']) for service in cat['services']) for cat in service_categories)} detailed services
"""))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding services: {str(e)}"))
