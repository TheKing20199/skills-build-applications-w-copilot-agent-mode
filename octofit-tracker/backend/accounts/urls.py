from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import accounts_home, login_view, register, profile_settings

urlpatterns = [
    path('', accounts_home, name='accounts_home'),
    path('login/', login_view, name='login'),
    path('register/', register, name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', profile_settings, name='profile_settings'),
]