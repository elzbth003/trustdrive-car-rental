from django.db import models
from django.conf import settings

class Car(models.Model):
    CAR_TYPES = (
        ('economy', 'Economy'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('luxury', 'Luxury'),
        ('van', 'Van'),
        ('hatchback', 'Hatchback'),
    )
    
    FUEL_TYPES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    )

    STATUS_CHOICES = (
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('service', 'In Service'),
        ('retired', 'Retired'),
    )

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    year = models.PositiveIntegerField(default=2024)
    registration_plate = models.CharField(max_length=20, unique=True, null=True)
    color = models.CharField(max_length=30, null=True)
    car_type = models.CharField(max_length=20, choices=CAR_TYPES)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPES)
    transmission = models.CharField(max_length=20, choices=(('manual', 'Manual'), ('automatic', 'Automatic')))
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(upload_to='cars/')
    interior_image_1 = models.ImageField(upload_to='cars/interiors/', null=True, blank=True)
    interior_image_2 = models.ImageField(upload_to='cars/interiors/', null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    seating_capacity = models.PositiveIntegerField(default=5)
    fuel_capacity = models.PositiveIntegerField(null=True, blank=True, help_text="Capacity in Liters")
    current_km = models.PositiveIntegerField(default=0)
    last_service_km = models.PositiveIntegerField(default=0)
    # branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name='fleet')
    trips_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def next_service_km(self):
        return self.last_service_km + 5000

    @property
    def is_service_due(self):
        return self.current_km >= self.next_service_km

    def __str__(self):
        return f"{self.brand} {self.name} ({self.registration_plate})"

    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 5.0  # Default for new cars
        return sum(r.rating for r in reviews) / reviews.count()

class Review(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.car.name} by {self.user.username}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car')

    def __str__(self):
        return f"{self.user.username} favorited {self.car.name}"

class MaintenanceLog(models.Model):
    LOG_TYPES = (
        ('service', 'Scheduled Service'),
        ('repair', 'Repair'),
        ('damage', 'Damage Report'),
    )
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='maintenance_logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPES)
    description = models.TextField()
    mileage_at_service = models.PositiveIntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    logged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and self.log_type == 'service':
            self.car.last_service_km = self.mileage_at_service
            self.car.save()
        if is_new and self.log_type == 'damage':
            self.car.status = 'service'
            self.car.save()
