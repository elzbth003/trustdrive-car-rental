# Car Rental Management System

A premium Car Rental Management System built with Django and MySQL.

## Features
- **Modern UI**: Dark-themed, glassmorphism design with responsive layout.
- **Three Core Modules**: 
  - **Admin**: Full control over fleet, users, and bookings.
  - **Staff**: Manage bookings and car availability.
  - **Customer**: Browse, search, filter, and book cars.
- **Booking Engine**: Date-based booking with overlap prevention and real-time cost calculation.
- **Payment Simulation**: Secure-looking payment gateway simulation.
- **Role-Based Dashboards**: Custom views and statistics based on user role.

## 🛠️ Setup Instructions

### 1. Database Configuration
1. Create a MySQL database named `car_rental_db`.
2. Update the `DATABASES` section in `core/settings.py` with your MySQL `USER` and `PASSWORD`.

### 2. Environment Setup
Make sure you have the required packages installed:
```bash
pip install django mysqlclient pillow
```

### 3. Migrations
Run the following commands to set up the database schema:
```bash
python manage.py makemigrations accounts cars bookings payments
python manage.py migrate
```

### 4. Create Admin User
Create a superuser to access the admin panel:
```bash
python manage.py createsuperuser
```
*Note: After creating, log in and change your 'role' to 'admin' in the Django Admin for full dashboard access.*

### 5. Run the Server
```bash
python manage.py run_server
```

## Project Structure
- `accounts/`: User management and role-based auth.
- `cars/`: Vehicle listings, search, and CRUD.
- `bookings/`: Booking logic and history.
- `payments/`: Payment processing simulation.
- `templates/`: Shared and app-specific modern templates.
- `static/css/base.css`: The custom design system.

## Technology Stack
- **Backend**: Django 6.0
- **Database**: MySQL
- **Frontend**: Bootstrap 5, Vanilla CSS, Inter Fonts, Bootstrap Icons
