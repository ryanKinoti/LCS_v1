# Laptop Care System (LCS_v1)

Laptop Care System (LCS_v1) is a comprehensive digital solution designed to manage and organize laptop repairs,
inventory, services, staff, customers, notifications, reports, and finances for a repair shop.

## Table of Contents

- [Project Structure](#project-structure)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Scripts](#scripts)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Laptop Repairs Management**: Manage and book laptop repairs.
- **Inventory Management**: Track laptops and parts inventory.
- **Services Management**: Manage services offered by the shop.
- **Staff and Customer Management**: Manage staff and customer information.
- **Notifications**: Send notifications to customers and staff.
- **Reports Generation**: Generate performance reports.
- **Financial Management**: Manage shop finances.

## Installation

### Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)
- Python (v3.1 or higher)
- Django (v5.1 or higher)

### Client Side

1. Navigate to the `client` directory:
   ```sh
   cd client
   ```
2. Install the dependencies:
   ```sh
   npm install
   ```

### Server Side
1. Navigate to the `client` directory (if you're still inside the client directory):
   ```sh
   cd ../server
   ```
2. Create a virtual environment:
   ```sh
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```sh
    venv\Scripts\activate
    ```
4. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```
5. Apply migrations:
    ```sh
    python manage.py makemigrations
    ```
    ```sh
    python manage.py migrate
    ```

## Usage
### Client Side
1. Navigate to the `client` directory:
   ```sh
   cd client
   ```
2. Start the development server:
   ```sh
    npm run dev
    ```
3. Open your browser and navigate to `http://localhost:3000`.
4. Login with the default credentials:
   - **Username**: admin
   - **Password**: admin

### Server Side
1. Navigate to the `server` directory:
   ```sh
   cd server
   ```
2. Start the Django server:
   ```sh
    python manage.py runserver
    ```
3. Open your browser and navigate to `http://localhost:8000/admin`.
4. Login with the default credentials:
   - **Username**: admin
   - **Password**: admin

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.