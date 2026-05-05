"""
Management command: python manage.py create_admin

Creates the initial Admin account securely without going through
the public registration form. Run this once during setup.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create the initial TrustDrive Admin account (run once during setup).'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email',    type=str, default='admin@trustdrive.com')
        parser.add_argument('--password', type=str, default=None)

    def handle(self, *args, **options):
        username = options['username']
        email    = options['email']
        password = options['password']

        if User.objects.filter(role='admin').exists():
            self.stdout.write(self.style.WARNING(
                'An admin account already exists. Skipping creation.'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Username '{username}' already taken. Skipping."
            ))
            return

        if not password:
            import getpass
            password = getpass.getpass('Enter admin password (min 8 chars): ')

        if len(password) < 8:
            self.stderr.write(self.style.ERROR('Password must be at least 8 characters.'))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        user.role = 'admin'
        user.save()

        self.stdout.write(self.style.SUCCESS(
            f"✓ Admin account '{username}' created successfully.\n"
            f"  Role: admin | Email: {email}\n"
            f"  Login at: /accounts/login/"
        ))
