from django.contrib import admin
from .models import Car, MaintenanceLog

admin.site.register(Car)
admin.site.register(MaintenanceLog)
