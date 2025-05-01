"""octofit_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from fitness.views import (
    octofit_home, house_detail, submit_activity, leaderboard, octocoach_response, accept_challenge, ask_coachbot, upload_progress_photo, list_progress_photos, daily_tip, save_onboarding,
    activity_feed, notifications_api, mark_notifications_read, user_profile_api, update_profile_api, analytics_api,
    send_friend_request, respond_friend_request, list_friends,
    create_team, join_team, list_teams,
    post_comment, list_comments, post_reaction, list_reactions,
    push_notification_poll, join_house, user_progress_api, friends, teams, activity_feed_page
)
from accounts.views import register

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", octofit_home, name="home"),
    path("register/", register, name="register"),
    path("house/<str:name>/", house_detail, name="house_detail"),
    path("submit-activity/", submit_activity, name="submit_activity"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("octocoach-response/", octocoach_response, name="octocoach_response"),
    path("accept-challenge/", accept_challenge, name="accept_challenge"),
    path("ask_coachbot/", ask_coachbot, name="ask_coachbot"),
    path("api/octocoach/ask/", ask_coachbot, name="octocoach_ask"),
    path("upload-progress-photo/", upload_progress_photo, name="upload_progress_photo"),
    path("list-progress-photos/", list_progress_photos, name="list_progress_photos"),
    path('api/daily-tip/', daily_tip, name='daily_tip'),
    path('api/save-onboarding/', save_onboarding, name='save_onboarding'),
    path('api/activity-feed/', activity_feed, name='activity_feed'),
    path('api/notifications/', notifications_api, name='notifications_api'),
    path('api/notifications/mark-read/', mark_notifications_read, name='mark_notifications_read'),
    path('api/user-profile/', user_profile_api, name='user_profile_api'),
    path('api/user-profile/update/', update_profile_api, name='update_profile_api'),
    path('api/analytics/', analytics_api, name='analytics_api'),
    path('api/friends/send/', send_friend_request, name='send_friend_request'),
    path('api/friends/respond/', respond_friend_request, name='respond_friend_request'),
    path('api/friends/list/', list_friends, name='list_friends'),
    path('api/teams/create/', create_team, name='create_team'),
    path('api/teams/join/', join_team, name='join_team'),
    path('api/teams/list/', list_teams, name='list_teams'),
    path('api/comments/post/', post_comment, name='post_comment'),
    path('api/comments/list/', list_comments, name='list_comments'),
    path('api/reactions/post/', post_reaction, name='post_reaction'),
    path('api/reactions/list/', list_reactions, name='list_reactions'),
    path('api/notifications/push/', push_notification_poll, name='push_notification_poll'),
    path('join_house/', join_house, name='join_house'),
    path('user_progress_api/', user_progress_api, name='user_progress_api'),
    path('user_profile_api/', user_profile_api, name='user_profile_api'),
    path("accounts/", include("accounts.urls")),  # Ensure accounts app URLs are included
    path('fitness/', include('fitness.urls')),
    path("friends/", friends, name="friends"),
    path("teams/", teams, name="teams"),
    path("activity-feed/", activity_feed_page, name="activity_feed_page"),
    path("send_friend_request/", lambda request: redirect('/api/friends/send/'), name="send_friend_request"),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


