# apps/inventory/management/commands/seed_inventory.py
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

    def generate_serial_number(self):
        """Generate a realistic serial number"""
        return f"{faker.random_letter().upper()}{faker.random_number(digits=2)}{faker.random_letter().upper()}{faker.random_number(digits=6)}"

    def handle(self, *args, **options):
        self.stdout.write("Creating inventory items...")

        # Predefined parts data for realism
        parts_data = [
            # Laptop Screens
            {
                'name': '15.6" FHD Laptop Screen',
                'model': 'LP156WF6-SPB1',
                'price': 12000,
                'quantity': faker.random_int(5, 15),
                'warranty_months': 12,
                'minimum_stock': 3
            },
            {
                'name': '14" HD Laptop Screen',
                'model': 'B140XTN07.2',
                'price': 10000,
                'quantity': faker.random_int(5, 15),
                'warranty_months': 12,
                'minimum_stock': 3
            },
            # Laptop Batteries
            {
                'name': 'Laptop Battery - ThinkPad Compatible',
                'model': '45N1001',
                'price': 6500,
                'quantity': faker.random_int(8, 20),
                'warranty_months': 6,
                'minimum_stock': 5
            },
            {
                'name': 'Laptop Battery - Dell Compatible',
                'model': 'WDX0R',
                'price': 7000,
                'quantity': faker.random_int(8, 20),
                'warranty_months': 6,
                'minimum_stock': 5
            },
            # Hard Drives
            {
                'name': '1TB SSD NVMe',
                'model': 'Samsung 970 EVO',
                'price': 15000,
                'quantity': faker.random_int(5, 12),
                'warranty_months': 24,
                'minimum_stock': 3
            },
            {
                'name': '500GB SSD SATA',
                'model': 'Samsung 860 EVO',
                'price': 8000,
                'quantity': faker.random_int(5, 12),
                'warranty_months': 24,
                'minimum_stock': 3
            },
            # RAM
            {
                'name': '8GB DDR4 RAM',
                'model': 'Crucial CT8G4DFS8266',
                'price': 4500,
                'quantity': faker.random_int(10, 25),
                'warranty_months': 12,
                'minimum_stock': 8
            },
            {
                'name': '16GB DDR4 RAM',
                'model': 'Crucial CT16G4DFD8266',
                'price': 9000,
                'quantity': faker.random_int(8, 20),
                'warranty_months': 12,
                'minimum_stock': 5
            },
            # Printer Parts
            {
                'name': 'Printer Maintenance Kit',
                'model': 'HP F2G76A',
                'price': 12000,
                'quantity': faker.random_int(3, 8),
                'warranty_months': 6,
                'minimum_stock': 2
            },
            # Desktop Parts
            {
                'name': 'Power Supply Unit 650W',
                'model': 'Corsair RM650x',
                'price': 11000,
                'quantity': faker.random_int(4, 10),
                'warranty_months': 24,
                'minimum_stock': 2
            }
        ]

        # Common laptop brands and models
        laptop_combinations = [
            ('Dell', ['Latitude 5420', 'XPS 13', 'Inspiron 15']),
            ('Lenovo', ['ThinkPad X1', 'IdeaPad 5', 'ThinkPad T14']),
            ('HP', ['EliteBook 840', 'ProBook 450', 'Pavilion 15']),
            ('Acer', ['Aspire 5', 'Swift 3', 'TravelMate P2']),
        ]

        try:
            with transaction.atomic():
                # Create shop inventory parts
                created_parts = []
                for part_data in parts_data:
                    part = DevicePart.objects.create(
                        name=part_data['name'],
                        model=part_data['model'],
                        serial_number=self.generate_serial_number(),
                        price=part_data['price'],
                        quantity=part_data['quantity'],
                        status=DeviceParts.IN_STOCK,
                        warranty_months=part_data['warranty_months'],
                        minimum_stock=part_data['minimum_stock']
                    )
                    created_parts.append(part)

                # Create some customer devices
                created_devices = []
                customers = User.objects.filter(is_staff=False, is_superuser=False)

                for customer in customers[:10]:  # Create devices for first 10 customers
                    brand, models = faker.random_element(laptop_combinations)
                    device = Device.objects.create(
                        customer=customer,
                        device_type=Devices.LAPTOP,
                        brand=brand,
                        model=faker.random_element(models),
                        serial_number=self.generate_serial_number(),
                        repair_status=faker.random_element([Devices.COMPLETED, Devices.IN_PROGRESS, None]),
                        sale_status=Devices.NEW
                    )
                    created_devices.append(device)

                    # Add some parts to customer devices
                    if faker.boolean(chance_of_getting_true=70):
                        DevicePart.objects.create(
                            customer_laptop=device,
                            name="Replacement Battery",
                            model=faker.random_element(["Original", "Compatible"]),
                            serial_number=self.generate_serial_number(),
                            quantity=1,
                            status=DeviceParts.USED
                        )

                self.stdout.write(self.style.SUCCESS(f"""
Successfully created:
- {len(created_parts)} inventory parts
- {len(created_devices)} customer devices
- Added parts to customer devices where applicable
"""))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding inventory: {str(e)}"))
