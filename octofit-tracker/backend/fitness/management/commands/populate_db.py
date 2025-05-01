from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fitness.models import House, UserProfile, FitnessActivity, HouseChallenge, HouseBadge
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate the database with demo data for all houses, users, activities, and challenges.'

    def handle(self, *args, **kwargs):
        # Create houses
        houses = [
            {'name': 'Kraken', 'mascot': '🐙', 'theme': 'Strength', 'description': 'Strong and bold sea creatures.'},
            {'name': 'Rayzor', 'mascot': '🐬', 'theme': 'Speed', 'description': 'Fast and competitive dolphins.'},
            {'name': 'Serene', 'mascot': '🐢', 'theme': 'Calm', 'description': 'Calm and consistent turtles.'},
            {'name': 'Montana', 'mascot': '🦑', 'theme': 'Playful', 'description': 'Playful and social squids.'},
        ]
        house_objs = {}
        for h in houses:
            obj, _ = House.objects.get_or_create(name=h['name'], defaults={
                'mascot': h['mascot'], 'theme': h['theme'], 'description': h['description']
            })
            house_objs[h['name']] = obj

        # Create demo users and assign to houses
        demo_users = [
            ('kraken_kate', 'Kraken'),
            ('rayzor_ron', 'Rayzor'),
            ('serene_sam', 'Serene'),
            ('montana_mia', 'Montana'),
        ]
        for username, house in demo_users:
            user, _ = User.objects.get_or_create(username=username, defaults={'password': 'demo1234'})
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.house = house_objs[house]
            profile.save()

        # Create activities for each user
        now_time = timezone.now()
        for username, house in demo_users:
            user = User.objects.get(username=username)
            for i in range(3):
                FitnessActivity.objects.create(
                    user=user,
                    activity_type=['Cardio', 'Strength', 'Yoga'][i % 3],
                    duration_minutes=30 + i * 10,
                    date=now_time.date() - timedelta(days=i)
                )

        # Create challenges for each house
        challenge_map = {
            'Kraken': ['Deadlift 100kg', 'Plank for 2 min'],
            'Rayzor': ['Sprint 400m', 'HIIT for 15 min'],
            'Serene': ['Yoga for 30 min', 'Meditate for 10 min'],
            'Montana': ['Dance for 20 min', 'Swim 500m']
        }
        for house, challenges in challenge_map.items():
            h = house_objs[house]
            for c in challenges:
                HouseChallenge.objects.get_or_create(house=h, description=c)

        # Create a badge for each house
        for house in house_objs.values():
            HouseBadge.objects.get_or_create(house=house, name=f"{house.name} Star", emoji=house.mascot, desc=f"Special badge for {house.name} house.")

        self.stdout.write(self.style.SUCCESS('Demo data populated for all houses, users, activities, and challenges.'))
