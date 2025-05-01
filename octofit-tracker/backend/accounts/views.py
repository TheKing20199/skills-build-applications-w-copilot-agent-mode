from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import RegisterForm, LoginForm, UserProfileForm
from fitness.models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

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
