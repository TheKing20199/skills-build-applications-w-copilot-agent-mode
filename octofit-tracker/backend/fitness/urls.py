from django.urls import path
from .views import fitness_home, submit_activity, accept_challenge, complete_challenge, suggest_challenge
from . import views

urlpatterns = [
    path('', fitness_home, name='fitness_home'),
    path('submit-activity/', submit_activity, name='submit_activity'),
    path('accept-challenge/', accept_challenge, name='accept_challenge'),
    path('complete-challenge/', complete_challenge, name='complete_challenge'),
    path('suggest-challenge/', suggest_challenge, name='suggest_challenge'),
    path('friends/', views.friends, name='friends'),
]