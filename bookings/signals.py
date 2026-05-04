from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
from .models import Booking
from cars.models import Car

@receiver(post_save, sender=Booking)
def handle_booking_status_change(sender, instance, created, **kwargs):
    """
    Automates car status and payment logic based on Booking status transitions.
    """
    car = instance.car

    # 1. On Booking status -> Confirmed
    if instance.status == 'confirmed':
        # Send confirmation email to customer
        send_mail(
            'Booking Confirmed - TrustDrive',
            f'Dear {instance.user.username}, your booking for {car.brand} {car.name} '
            f'from {instance.start_date} to {instance.end_date} is confirmed.',
            'noreply@trustdrive.com',
            [instance.user.email],
            fail_silently=True,
        )

    # 2. On Booking status -> Active (Check-out)
    elif instance.status == 'active':
        car.status = 'rented'
        car.save()
        if not instance.actual_start:
            instance.actual_start = timezone.now()
            instance.save(update_fields=['actual_start'])

    # 3. On Booking status -> Completed (Return)
    elif instance.status == 'completed':
        # Only set back to available if not already in service (e.g. from damage log)
        if car.status != 'service':
            car.status = 'available'
        car.save()
        
        if not instance.actual_end:
            instance.actual_end = timezone.now()
            instance.save(update_fields=['actual_end'])

        # Update final amount if payment exists
        if hasattr(instance, 'payment'):
            # Calculate actual duration based on dates
            duration = (instance.actual_end.date() - instance.start_date).days
            if duration <= 0: duration = 1
            instance.payment.amount = car.daily_rate * duration
            instance.payment.save()

    # 4. On Booking status -> Cancelled
    elif instance.status == 'cancelled':
        car.status = 'available'
        car.save()
