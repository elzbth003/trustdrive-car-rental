import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cars.models import Car

cars_to_add = [
    {
        'brand': 'Lamborghini',
        'name': 'Huracán Evo',
        'car_type': 'luxury',
        'fuel_type': 'petrol',
        'transmission': 'automatic',
        'price_per_day': 1200.00,
        'description': 'Experience the thrill of V10 power and unmistakable Italian design.',
        'image': None # User will need to upload or I can use placeholder URLs if I had them
    },
    {
        'brand': 'Rolls-Royce',
        'name': 'Ghost',
        'car_type': 'luxury',
        'fuel_type': 'petrol',
        'transmission': 'automatic',
        'price_per_day': 1500.00,
        'description': 'The pinnacle of luxury. Silent, smooth, and commanding.',
        'image': None
    },
    {
        'brand': 'Porsche',
        'name': '911 Carrera S',
        'car_type': 'suv', # Just using available types, maybe luxury is better
        'fuel_type': 'petrol',
        'transmission': 'automatic',
        'price_per_day': 800.00,
        'description': 'The timeless sports car. Precision engineering for the driving enthusiast.',
        'image': None
    },
    {
        'brand': 'Tesla',
        'name': 'Model S Plaid',
        'car_type': 'sedan',
        'fuel_type': 'electric',
        'transmission': 'automatic',
        'price_per_day': 500.00,
        'description': 'Insane acceleration and cutting-edge technology.',
        'image': None
    },
    {
        'brand': 'Mercedes-Benz',
        'name': 'G63 AMG',
        'car_type': 'suv',
        'fuel_type': 'petrol',
        'transmission': 'automatic',
        'price_per_day': 950.00,
        'description': 'Unmatched off-road capability combined with high-performance AMG spirit.',
        'image': None
    }
]

for car_data in cars_to_add:
    car, created = Car.objects.get_or_create(
        brand=car_data['brand'],
        name=car_data['name'],
        defaults=car_data
    )
    if created:
        print(f"Added {car.brand} {car.name}")
    else:
        print(f"{car.brand} {car.name} already exists")
