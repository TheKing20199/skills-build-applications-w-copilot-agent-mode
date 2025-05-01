from django.test import TestCase, Client
from django.contrib.auth.models import User
from fitness.models import House, HouseChallenge, ChallengeSuggestion, UserProfile, AcceptedChallenge

class OctoFitFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.house = House.objects.create(name="Kraken", mascot="🐙", color="#1e90ff", theme="Sea Power", description="Unleash your inner sea monster!")
        self.challenge = HouseChallenge.objects.create(house=self.house, description="Plank for 1 minute")
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.house = self.house
        self.user_profile.save()

    def test_registration_and_login(self):
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after registration

    def test_activity_logging(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post('/fitness/submit-activity/', {
            'activity_type': 'Running',
            'duration_minutes': 30,
            'date': '2025-04-29',
        })
        self.assertIn(response.status_code, [200, 302])

    def test_challenge_accept_and_complete(self):
        self.client.login(username="testuser", password="testpass")
        # Accept challenge
        response = self.client.post('/fitness/accept-challenge/', content_type='application/json', data='{"description":"Plank for 1 minute","xp":10}')
        self.assertEqual(response.status_code, 200)
        # Ensure the challenge is accepted before completing
        from fitness.models import AcceptedChallenge
        self.assertTrue(AcceptedChallenge.objects.filter(user=self.user, challenge_description="Plank for 1 minute", completed_at__isnull=True).exists())
        # Complete challenge
        response = self.client.post('/fitness/complete-challenge/', content_type='application/json', data='{"description":"Plank for 1 minute","xp":10}')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(AcceptedChallenge.objects.filter(user=self.user, challenge_description="Plank for 1 minute", completed_at__isnull=False).exists())

    def test_suggest_challenge(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.post('/fitness/suggest-challenge/', {
            'description': 'Swim 10 laps',
            'house_id': self.house.id
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ChallengeSuggestion.objects.filter(description='Swim 10 laps', house=self.house).exists())
