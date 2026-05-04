import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.apps import apps
print("Apps:", [app.label for app in apps.get_app_configs()])

from django.db import connection
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    print("Tables:", [row[0] for row in cursor.fetchall()])
