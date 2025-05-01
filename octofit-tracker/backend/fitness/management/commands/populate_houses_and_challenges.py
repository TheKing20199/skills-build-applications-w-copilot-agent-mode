from django.core.management.base import BaseCommand
from fitness.models import House, HouseChallenge

class Command(BaseCommand):
    help = 'Pre-populate houses and unique, themed challenges for each house.'

    def handle(self, *args, **kwargs):
        house_data = [
            {
                'name': 'Kraken',
                'mascot': '🐙',
                'color': '#1e90ff',
                'theme': 'Sea Power',
                'description': 'Unleash your inner sea monster!',
                'challenges': [
                    'Plank for 1 minute',
                    'Swim 10 laps',
                    'Underwater breath hold for 30 seconds',
                    'Crab walk 20 meters',
                    'Sea shanty dance challenge',
                ]
            },
            {
                'name': 'Montana',
                'mascot': '🦅',
                'color': '#228B22',
                'theme': 'Mountain Endurance',
                'description': 'Rise above with mountain strength!',
                'challenges': [
                    'Hike 2 miles',
                    'Do 20 mountain climbers',
                    'Yoga at sunrise',
                    'Nature photo walk',
                    'Summit sprint (run up stairs/hill)',
                ]
            },
            {
                'name': 'Razor',
                'mascot': '🦈',
                'color': '#c0392b',
                'theme': 'Sharp Focus',
                'description': 'Cut through limits with razor focus!',
                'challenges': [
                    'Shadow boxing for 3 minutes',
                    'Jump rope 100 times',
                    'Balance on one leg for 1 minute',
                    'Speed run 400m',
                    'Push-up pyramid (1-2-3-2-1)',
                ]
            },
            {
                'name': 'Serene',
                'mascot': '🦋',
                'color': '#8e44ad',
                'theme': 'Calm & Flexibility',
                'description': 'Find your flow and peace!',
                'challenges': [
                    '5 min guided meditation',
                    'Hold tree pose for 1 minute',
                    'Stretch for 10 minutes',
                    'Mindful walk outdoors',
                    'Write a gratitude list',
                ]
            },
        ]

        for h in house_data:
            house, _ = House.objects.get_or_create(
                name=h['name'], defaults={
                    'mascot': h['mascot'],
                    'color': h['color'],
                    'theme': h['theme'],
                    'description': h['description'],
                })
            for desc in h['challenges']:
                HouseChallenge.objects.get_or_create(house=house, description=desc)
        self.stdout.write(self.style.SUCCESS('Houses and challenges pre-populated!'))
