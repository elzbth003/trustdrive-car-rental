from django.core.management.base import BaseCommand
from django.utils import timezone
from cars.models import Car
from django.core.mail import send_mail

from django.db.models import F

class Command(BaseCommand):
    help = 'Checks for vehicles requiring maintenance and sends alerts to admins.'

    def handle(self, *args, **options):
        overdue_cars = Car.objects.filter(current_km__gte=F('last_service_km') + 5000)
        
        if overdue_cars.exists():
            car_list = "\n".join([f"- {car.brand} {car.name} ({car.registration_plate}): {car.current_km}km" for car in overdue_cars])
            
            # In a real scenario, you'd send this to staff emails
            self.stdout.write(self.style.SUCCESS(f"Found {overdue_cars.count()} cars needing maintenance."))
            
            # Simulated Email logic
            # send_mail(
            #     'Maintenance Alert - TrustDrive',
            #     f'The following vehicles require immediate service:\n\n{car_list}',
            #     'system@trustdrive.com',
            #     ['staff@trustdrive.com'],
            # )
        else:
            self.stdout.write(self.style.SUCCESS("All vehicles are within service intervals."))
