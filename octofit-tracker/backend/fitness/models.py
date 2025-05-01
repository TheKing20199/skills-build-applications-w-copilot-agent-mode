from django.db import models
from django.contrib.auth.models import User
from fitness.utils.agent_logic import calculate_streak
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import now
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q
from datetime import date

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey('ActivityFeedItem', on_delete=models.CASCADE, null=True, blank=True)
    photo_url = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.text[:30]}..."

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending','Pending'),('accepted','Accepted'),('declined','Declined')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('from_user', 'to_user')
    def __str__(self):
        return f"{self.from_user} -> {self.to_user} ({self.status})"

class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendship_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendship_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user1', 'user2')
    def __str__(self):
        return f"{self.user1} <-> {self.user2}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name

class TeamMembership(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('team', 'user')
    def __str__(self):
        return f"{self.user} in {self.team}"

class House(models.Model):
    name = models.CharField(max_length=50)
    mascot = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    points = models.IntegerField(default=0)
    confetti_shown = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')
    theme = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return self.name

class HouseActivity(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='activities')
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.house.name}: {self.description}"

class HouseChallenge(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='challenges')
    description = models.CharField(max_length=255)
    xp = models.PositiveIntegerField(default=10)
    canonical_activity = models.CharField(max_length=50, blank=True, null=True, help_text="Normalized activity type for robust matching (e.g. 'walk', 'yoga')")

    def __str__(self):
        return f"{self.house.name}: {self.description}"

class HouseBadge(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name='badges')
    name = models.CharField(max_length=100)
    emoji = models.CharField(max_length=10)
    desc = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.house.name}: {self.name}"

class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_index=True)
    badge = models.ForeignKey(HouseBadge, on_delete=models.CASCADE, db_index=True)
    earned_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Student(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    house = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class FitnessActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    activity_type = models.CharField(max_length=50, db_index=True)
    duration_minutes = models.PositiveIntegerField()
    date = models.DateField(default=date.today, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update house points when a fitness activity is saved
        profile = getattr(self.user, 'userprofile', None)
        if profile and profile.house:
            profile.house.points += self.duration_minutes // 10  # Example: 1 point for every 10 minutes
            profile.house.save()

        # Calculate and log the user's streak
        if self.user:
            streak = calculate_streak(self.user)
            print(f"User {self.user.username} has a streak of {streak} days.")  # Replace with actual logging or notification logic

            # Update the user's streak count in their profile
            user_profile = self.user.userprofile
            user_profile.streak_count = streak
            user_profile.save()

            # Mark recommendations as completed if the activity matches
            RecommendationLog.objects.filter(user=self.user, recommendation_type=self.activity_type, is_completed=False).update(is_completed=True, date_completed=now())

        # Mark challenge as completed if activity matches a challenge (robust logic)
        if self.user and hasattr(self.user, 'userprofile') and self.user.userprofile.house:
            house = self.user.userprofile.house
            from fitness.models import HouseChallenge, AcceptedChallenge
            # Normalize activity_type
            act = self.activity_type.strip().lower()
            # Try canonical_activity match first
            for challenge in house.challenges.all():
                if challenge.canonical_activity:
                    if act == challenge.canonical_activity.strip().lower():
                        AcceptedChallenge.objects.filter(user=self.user, challenge_description=challenge.description, completed_at__isnull=True).update(completed_at=now())
                else:
                    # Fallback: improved substring/keyword match
                    if act in challenge.description.lower() or challenge.description.lower() in act:
                        AcceptedChallenge.objects.filter(user=self.user, challenge_description=challenge.description, completed_at__isnull=True).update(completed_at=now())
        # Automate badge awarding after activity log
        if self.user:
            from .models import check_and_award_badges, check_and_award_rewards
            check_and_award_badges(self.user)
            check_and_award_rewards(self.user)

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"

class TeacherChallenge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class HousePoints(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)

class ActivityFeedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='targeted_feed_items')
    created_at = models.DateTimeField(auto_now_add=True)
    house = models.ForeignKey('House', on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} {self.action} {self.description} at {self.created_at}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    notif_type = models.CharField(max_length=50, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}: {self.message} ({'read' if self.is_read else 'unread'})"

# Extend UserProfile for avatar and bio/interests
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    streak_count = models.PositiveIntegerField(default=0)  # Store the user's streak count
    house = models.ForeignKey('House', on_delete=models.SET_NULL, null=True, blank=True)
    checklist_state = models.TextField(null=True, blank=True)
    # --- New fields for daily OctoCoach tips ---
    last_tip_date = models.DateField(null=True, blank=True)
    last_tip_text = models.TextField(null=True, blank=True)
    # --- Onboarding state fields ---
    onboarding_complete = models.BooleanField(default=False)
    onboarding_answers = models.JSONField(null=True, blank=True)
    avatar = models.CharField(max_length=255, blank=True, default='')  # emoji or image URL
    bio = models.TextField(blank=True, default='')
    interests = models.CharField(max_length=255, blank=True, default='')
    email_reminders = models.BooleanField(default=True)  # Opt-in for email reminders
    BOT_PERSONA_CHOICES = [
        ("arnold", "Classic Arnold"),
        ("jennifer", "Jennifer Aniston"),
        ("katy", "Katy Perry"),
        ("mel", "Mel Gibson"),
    ]
    bot_persona = models.CharField(max_length=20, choices=BOT_PERSONA_CHOICES, default="arnold")
    # --- Journey/OctoCoach fields ---
    has_seen_onboarding = models.BooleanField(default=False)
    house_joined_at = models.DateTimeField(null=True, blank=True)
    first_activity_logged_at = models.DateTimeField(null=True, blank=True)
    last_streak_milestone = models.PositiveIntegerField(default=0)
    last_points_milestone = models.PositiveIntegerField(default=0)
    last_challenge_prompted = models.CharField(max_length=255, blank=True, default='')
    last_octocoach_message = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class RecommendationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendation_type = models.CharField(max_length=100)
    is_completed = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.recommendation_type} - {'Completed' if self.is_completed else 'Pending'}"

class AcceptedChallenge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    challenge_description = models.CharField(max_length=255, db_index=True)
    xp_points = models.PositiveIntegerField(default=0)
    accepted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)

    def __str__(self):
        status = "Completed" if self.completed_at else "Pending"
        return f"{self.user.username} - {self.challenge_description} ({status})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

def check_and_award_badges(user):
    from .models import HouseBadge, UserBadge, AcceptedChallenge, UserProfile
    import re
    profile = UserProfile.objects.get(user=user)
    house = profile.house
    if not house:
        return
    completed_count = AcceptedChallenge.objects.filter(user=user, completed_at__isnull=False).count()
    for badge in HouseBadge.objects.filter(house=house):
        # Generic: "Complete N challenges"
        match = re.match(r".*(\d+)[+]? challenge", badge.name, re.IGNORECASE)
        if match:
            n = int(match.group(1))
            if completed_count >= n and not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)
                continue
        # Generic: "N-day streak"
        match = re.match(r".*(\d+)[- ]?day streak", badge.name, re.IGNORECASE)
        if match:
            n = int(match.group(1))
            if profile.streak_count >= n and not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)
                continue
        # Custom logic for special badges (examples)
        if badge.name == "Zen Guru":
            yoga_challenges = [c.description for c in house.challenges.filter(description__icontains='yoga') | house.challenges.filter(description__icontains='stretch')]
            completed = AcceptedChallenge.objects.filter(user=user, challenge_description__in=yoga_challenges, completed_at__isnull=False).count()
            if yoga_challenges and completed == len(yoga_challenges) and not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)
        if badge.name == "Trailblazer":
            from .models import FitnessActivity
            walk_count = FitnessActivity.objects.filter(user=user, activity_type__icontains='walk').count()
            if walk_count >= 7 and not UserBadge.objects.filter(user=user, badge=badge).exists():
                UserBadge.objects.create(user=user, badge=badge)
        # Add more custom logic as needed

def delete_accepted_challenges_on_house_delete(sender, instance, **kwargs):
    from .models import AcceptedChallenge, UserProfile
    user_ids = UserProfile.objects.filter(house=instance).values_list('user_id', flat=True)
    AcceptedChallenge.objects.filter(user_id__in=user_ids).delete()

pre_delete.connect(delete_accepted_challenges_on_house_delete, sender=House)

class Reaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.ForeignKey('ActivityFeedItem', on_delete=models.CASCADE, null=True, blank=True)
    photo_url = models.CharField(max_length=255, blank=True, null=True)
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}: {self.emoji}"

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Emoji or icon name")
    unlock_points = models.PositiveIntegerField(default=0, help_text="Points needed to unlock")
    unlock_streak = models.PositiveIntegerField(default=0, help_text="Streak needed to unlock")
    unlock_challenges = models.PositiveIntegerField(default=0, help_text="Challenges completed to unlock")

    def __str__(self):
        return self.name

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'reward')

    def __str__(self):
        return f"{self.user.username} - {self.reward.name}"

def check_and_award_rewards(user):
    from .models import Reward, UserReward, AcceptedChallenge, UserProfile
    profile = UserProfile.objects.get(user=user)
    points = profile.house.points if profile.house else 0
    streak = profile.streak_count
    completed_challenges = AcceptedChallenge.objects.filter(user=user, completed_at__isnull=False).count()
    for reward in Reward.objects.all():
        if (
            (reward.unlock_points and points >= reward.unlock_points) or
            (reward.unlock_streak and streak >= reward.unlock_streak) or
            (reward.unlock_challenges and completed_challenges >= reward.unlock_challenges)
        ):
            if not UserReward.objects.filter(user=user, reward=reward).exists():
                UserReward.objects.create(user=user, reward=reward)

# Call check_and_award_rewards in FitnessActivity.save and challenge completion

class ChallengeSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    house = models.ForeignKey('House', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user.username} ({self.house.name}): {self.description}"

class OctoCoachChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='octocoach_chats')
    sender = models.CharField(max_length=10, choices=[('user', 'User'), ('bot', 'Bot')])
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    context_type = models.CharField(max_length=32, blank=True, default='')  # e.g. 'onboarding', 'activity', etc.

    def __str__(self):
        return f"{self.user.username} [{self.sender}] {self.timestamp:%Y-%m-%d %H:%M}: {self.message[:40]}"
