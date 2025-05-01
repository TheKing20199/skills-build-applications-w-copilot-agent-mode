from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.mail import send_mail
from fitness.models import UserProfile, FitnessActivity
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Send daily email reminders to users who have opted in.'

    def handle(self, *args, **kwargs):
        today = date.today()
        users = User.objects.filter(userprofile__email_reminders=True, is_active=True)
        for user in users:
            # Check if user has logged an activity today
            if not FitnessActivity.objects.filter(user=user, date=today).exists():
                subject = '🏋️‍♂️ OctoFit: Don’t forget to log your activity today!'
                message = (
                    f"Hi {user.username},\n\n"
                    "Keep your streak going! Log your workout or activity in OctoFit today to earn points and badges.\n\n"
                    "Visit your dashboard: https://[YOUR_APP_URL]/\n\n"
                    "Stay strong! 💪\nOctoFit Team"
                )
                send_mail(
                    subject,
                    message,
                    'noreply@octofit.com',
                    [user.email],
                    fail_silently=True,
                )
        self.stdout.write(self.style.SUCCESS('Email reminders sent.'))
