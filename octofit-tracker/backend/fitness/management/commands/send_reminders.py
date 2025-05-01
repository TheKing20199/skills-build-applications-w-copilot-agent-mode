from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from fitness.models import UserProfile, FitnessActivity
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Send daily email reminders to users who opted in and have not logged an activity today.'

    def handle(self, *args, **options):
        today = date.today()
        users = User.objects.filter(userprofile__email_reminders=True, is_active=True)
        count = 0
        for user in users:
            if not FitnessActivity.objects.filter(user=user, date=today).exists():
                email = user.email
                if not email:
                    continue
                send_mail(
                    subject='⏰ Don’t lose your OctoFit streak!',
                    message=(
                        f"Hi {user.username},\n\n"
                        "This is your friendly OctoFit reminder to log a workout today and keep your streak alive!\n\n"
                        "Log your activity now: https://octofit.example.com/\n\n"
                        "Stay active! 🐙"
                    ),
                    from_email=None,  # Use DEFAULT_FROM_EMAIL
                    recipient_list=[email],
                    fail_silently=False,
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Sent reminders to {count} users."))
