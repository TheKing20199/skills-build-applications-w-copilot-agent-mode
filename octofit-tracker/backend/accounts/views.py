from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import RegisterForm, LoginForm, UserProfileForm
from fitness.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
import random, string

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to the home page after registration
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                profile, _ = UserProfile.objects.get_or_create(user=user)
                login(request, user)
                # Redirect to the user's house page if house is set
                if hasattr(profile, 'house') and profile.house:
                    return redirect('house_detail', name=profile.house.name.lower())
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def guest_login(request):
    if request.user.is_authenticated:
        return redirect('/')
    # Create a unique guest username and display name
    rand_id = ''.join(random.choices(string.digits, k=4))
    username = f'guest_{rand_id}'
    display_name = f'Guest{rand_id}'
    password = User.objects.make_random_password()
    user = User.objects.create_user(username=username, password=password)
    user.save()
    # Assign a random house to the guest user
    from fitness.models import House, UserProfile, HouseChallenge
    houses = list(House.objects.all())
    if houses:
        import random as pyrandom
        house = pyrandom.choice(houses)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.house = house
        profile.onboarding_complete = True
        profile.avatar = '👤'
        profile.bio = 'Temporary guest account'
        profile.save()
        # Ensure the house has at least one challenge
        if not house.challenges.exists():
            HouseChallenge.objects.create(house=house, description="Demo Challenge: Log any activity today!")
    user.first_name = display_name
    user.save()
    login(request, user)
    return redirect('/')

@login_required
def profile_settings(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('profile_settings')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/profile_settings.html', {'form': form})

def accounts_home(request):
    return HttpResponse("<h2>Accounts Home</h2><p>Welcome to the accounts section. Try /login/ or /register/.</p>")
