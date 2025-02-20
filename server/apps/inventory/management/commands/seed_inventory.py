# apps/inventory/management/commands/seed_inventory.py
import json
import os
import random
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from django.contrib.auth import get_user_model

from apps.inventory.models import Device, DevicePart
from utils.constants import Devices, DeviceParts

User = get_user_model()
faker = Faker()


class Command(BaseCommand):
    help = 'Seed the database with inventory items and device parts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json-file',
            type=str,
            default=os.path.join(
                settings.BASE_DIR,
                'apps',
                'inventory',
                'management',
                'commands',
                'data.json'
            ),
            help='Path to the JSON file containing inventory data'
        )

    def generate_serial_number(self):
        """Generate a realistic serial number"""
        return f"{faker.random_letter().upper()}{faker.random_number(digits=2)}{faker.random_letter().upper()}{faker.random_number(digits=6)}"

    def create_customer_device_parts(self, device, json_data):
        """Create parts specific to a customer's device"""
        # Add RAM (either 1 or 2 sticks)
        ram_count = random.randint(1, 2)
        ram_type = random.choice(json_data['parts_data']['ram'])
        for _ in range(ram_count):
            DevicePart.objects.create(
                customer_laptop=device,
                name=ram_type['name'],
                model=ram_type['model'],
                serial_number=self.generate_serial_number(),
                quantity=1,
                status=DeviceParts.USED
            )

        # Add Battery (always 1)
        battery_type = random.choice(json_data['parts_data']['laptop_batteries'])
        DevicePart.objects.create(
            customer_laptop=device,
            name=battery_type['name'],
            model=battery_type['model'],
            serial_number=self.generate_serial_number(),
            quantity=1,
            status=DeviceParts.USED
        )

        # Add Storage (HDD, SSD, or both)
        storage_choice = random.choice(['hdd', 'ssd', 'both'])
        if storage_choice in ['hdd', 'both']:
            hdd_type = random.choice(json_data['parts_data']['storage_drives']['hdd'])
            DevicePart.objects.create(
                customer_laptop=device,
                name=hdd_type['name'],
                model=hdd_type['model'],
                serial_number=self.generate_serial_number(),
                quantity=1,
                status=DeviceParts.USED
            )

        if storage_choice in ['ssd', 'both']:
            ssd_type = random.choice(json_data['parts_data']['storage_drives']['ssd'])
            DevicePart.objects.create(
                customer_laptop=device,
                name=ssd_type['name'],
                model=ssd_type['model'],
                serial_number=self.generate_serial_number(),
                quantity=1,
                status=DeviceParts.USED
            )

    def handle(self, *args, **options):
        self.stdout.write("Creating inventory items...")

        try:
            # Load JSON data
            with open(options['json_file'], 'r') as f:
                json_data = json.load(f)

            with transaction.atomic():
                created_parts = []

                # Create shop inventory parts
                for category in json_data['parts_data'].values():
                    # Handle nested storage drives structure
                    if isinstance(category, dict):
                        for subcategory in category.values():
                            for part_data in subcategory:
                                part = DevicePart.objects.create(
                                    name=part_data['name'],
                                    model=part_data['model'],
                                    serial_number=self.generate_serial_number(),
                                    price=part_data['price'],
                                    quantity=random.randint(*part_data['quantity_range']),
                                    status=DeviceParts.IN_STOCK,
                                    warranty_months=part_data['warranty_months'],
                                    minimum_stock=part_data['minimum_stock']
                                )
                                created_parts.append(part)
                    # Handle regular list structure
                    elif isinstance(category, list):
                        for part_data in category:
                            part = DevicePart.objects.create(
                                name=part_data['name'],
                                model=part_data['model'],
                                serial_number=self.generate_serial_number(),
                                price=part_data['price'],
                                quantity=random.randint(*part_data['quantity_range']),
                                status=DeviceParts.IN_STOCK,
                                warranty_months=part_data['warranty_months'],
                                minimum_stock=part_data['minimum_stock']
                            )
                            created_parts.append(part)

                # Create customer devices
                created_devices = []
                customers = User.objects.filter(is_staff=False, is_superuser=False)

                for customer in customers[:10]:  # Create devices for first 10 customers
                    brand_data = random.choice(json_data['laptop_brands'])
                    device = Device.objects.create(
                        customer=customer,
                        device_type=Devices.LAPTOP,
                        brand=brand_data['brand'],
                        model=random.choice(brand_data['models']),
                        serial_number=self.generate_serial_number(),
                        repair_status=random.choice([Devices.COMPLETED, Devices.IN_PROGRESS, None]),
                        sale_status=Devices.NEW
                    )
                    created_devices.append(device)

                    # Create device-specific parts
                    self.create_customer_device_parts(device, json_data)

                self.stdout.write(self.style.SUCCESS(f"""
Successfully created:
- {len(created_parts)} inventory parts
- {len(created_devices)} customer devices with:
  * RAM (1-2 sticks per device)
  * Battery (1 per device)
  * Storage (HDD and/or SSD per device)
"""))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"JSON file not found: {options['json_file']}"))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON format: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding inventory: {str(e)}"))
