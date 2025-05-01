from django.core.management.base import BaseCommand
from fitness.models import House, HouseActivity, HouseChallenge, UserProfile, UserBadge, HouseBadge
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populate demo data: houses, activities, challenges, demo users, badges.'

    def handle(self, *args, **options):
        # Houses
        houses = [
            {"name": "Kraken", "mascot": "🐙", "color": "#1976d2", "theme": "Sea Power", "description": "The mighty Kraken house!"},
            {"name": "Montana", "mascot": "🏔️", "color": "#43a047", "theme": "Mountain Strength", "description": "Montana house stands tall."},
            {"name": "Razor", "mascot": "🦈", "color": "#e53935", "theme": "Sharp Focus", "description": "Razor house is fierce."},
            {"name": "Serene", "mascot": "🧘", "color": "#8e24aa", "theme": "Calm Mind", "description": "Serene house is zen."},
        ]
        for h in houses:
            house, _ = House.objects.get_or_create(name=h["name"], defaults={
                "mascot": h["mascot"], "color": h["color"], "theme": h["theme"], "description": h["description"]
            })
            # Activities
            for i in range(1, 4):
                HouseActivity.objects.get_or_create(house=house, description=f"{h['theme']} Activity {i}")
            # Challenges
            for i in range(1, 3):
                HouseChallenge.objects.get_or_create(house=house, description=f"{h['theme']} Challenge {i}")
            # Demo user for each house
            username = f"demo_{h['name'].lower()}"
            user, _ = User.objects.get_or_create(username=username, defaults={
                "email": f"{username}@test.com", "first_name": h["name"], "last_name": "User"
            })
            user.set_password("TestPassword123!")
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.house = house
            profile.save()
        # Also keep the original octofittestuser for Kraken
        user, _ = User.objects.get_or_create(username="octofittestuser", defaults={
            "email": "octofittestuser@test.com", "first_name": "Test", "last_name": "User"
        })
        user.set_password("TestPassword123!")
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.house = House.objects.get(name="Kraken")
        profile.save()
        self.stdout.write(self.style.SUCCESS('Demo data populated: houses, activities, challenges, demo users for each house.'))
