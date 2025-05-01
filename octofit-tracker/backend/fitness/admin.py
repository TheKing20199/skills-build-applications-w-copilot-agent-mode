from django.contrib import admin
from .models import (
    House, HouseActivity, HouseChallenge, HouseBadge, UserBadge, ChallengeSuggestion,
    FitnessActivity, UserProfile, Team, TeamMembership, Notification, ActivityFeedItem,
    Reward, UserReward, Comment, Reaction
)

class HouseActivityInline(admin.TabularInline):
    model = HouseActivity
    extra = 1

class HouseChallengeInline(admin.TabularInline):
    model = HouseChallenge
    extra = 1

class HouseBadgeInline(admin.TabularInline):
    model = HouseBadge
    extra = 1

@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    inlines = [HouseActivityInline, HouseChallengeInline, HouseBadgeInline]
    list_display = ("name", "theme", "color", "points")

@admin.register(HouseActivity)
class HouseActivityAdmin(admin.ModelAdmin):
    list_display = ("house", "description")

@admin.register(HouseChallenge)
class HouseChallengeAdmin(admin.ModelAdmin):
    list_display = ("house", "description", "xp")

@admin.register(HouseBadge)
class HouseBadgeAdmin(admin.ModelAdmin):
    list_display = ("house", "name", "emoji", "desc")

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ("user", "badge", "earned_at")

@admin.register(ChallengeSuggestion)
class ChallengeSuggestionAdmin(admin.ModelAdmin):
    list_display = ('description', 'user', 'house', 'created_at', 'reviewed', 'approved')
    list_filter = ('house', 'reviewed', 'approved')
    search_fields = ('description', 'user__username', 'house__name')
    actions = ['approve_suggestions', 'move_approved_to_challenges']

    def approve_suggestions(self, request, queryset):
        updated = queryset.update(reviewed=True, approved=True)
        self.message_user(request, f"{updated} suggestion(s) approved.")
    approve_suggestions.short_description = "Approve selected suggestions"

    def move_approved_to_challenges(self, request, queryset):
        from .models import HouseChallenge
        count = 0
        for suggestion in queryset.filter(approved=True):
            obj, created = HouseChallenge.objects.get_or_create(
                house=suggestion.house,
                description=suggestion.description
            )
            if created:
                count += 1
        self.message_user(request, f"{count} approved suggestion(s) moved to HouseChallenge.")
    move_approved_to_challenges.short_description = "Move approved suggestions to HouseChallenge"

@admin.register(FitnessActivity)
class FitnessActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "duration_minutes", "date", "created_at")
    list_filter = ("activity_type", "date")
    search_fields = ("user__username", "activity_type")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "house", "streak_count", "onboarding_complete")
    list_filter = ("house", "onboarding_complete")
    search_fields = ("user__username",)
    ordering = ("user__username",)
    readonly_fields = ("streak_count",)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
    search_fields = ("name", "created_by__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(TeamMembership)
class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("team", "user", "joined_at")
    list_filter = ("team",)
    search_fields = ("user__username", "team__name")
    ordering = ("-joined_at",)
    readonly_fields = ("joined_at",)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "notif_type", "is_read", "created_at")
    list_filter = ("notif_type", "is_read")
    search_fields = ("user__username", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(ActivityFeedItem)
class ActivityFeedItemAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "description", "created_at", "house")
    list_filter = ("house",)
    search_fields = ("user__username", "action", "description")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "unlock_points", "unlock_streak", "unlock_challenges")
    search_fields = ("name",)
    ordering = ("name",)

@admin.register(UserReward)
class UserRewardAdmin(admin.ModelAdmin):
    list_display = ("user", "reward", "unlocked_at")
    list_filter = ("reward",)
    search_fields = ("user__username", "reward__name")
    ordering = ("-unlocked_at",)
    readonly_fields = ("unlocked_at",)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "activity", "photo_url", "text", "created_at")
    search_fields = ("user__username", "text")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ("user", "activity", "photo_url", "emoji", "created_at")
    search_fields = ("user__username", "emoji")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
