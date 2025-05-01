from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from fitness.models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'interests', 'email_reminders', 'bot_persona']
        widgets = {
            'avatar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Avatar (emoji or URL)'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Short bio', 'rows': 2}),
            'interests': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Interests'}),
            'email_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bot_persona': forms.Select(attrs={'class': 'form-control'}),
        }