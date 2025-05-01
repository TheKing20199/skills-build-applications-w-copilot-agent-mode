from django import forms
from .models import FitnessActivity

class FitnessActivityForm(forms.ModelForm):
    ACTIVITY_CHOICES = [
        ('Running', 'Running'),
        ('Walking', 'Walking'),
        ('Cycling', 'Cycling'),
        ('Swimming', 'Swimming'),
        ('Strength', 'Strength Training'),
        ('Yoga', 'Yoga'),
        ('Other', 'Other'),
    ]
    activity_type = forms.ChoiceField(choices=ACTIVITY_CHOICES, widget=forms.Select(attrs={'title': 'Select the type of activity you performed'}))
    duration_minutes = forms.IntegerField(min_value=1, widget=forms.NumberInput(attrs={'placeholder': 'Enter duration in minutes', 'title': 'How many minutes did you do this activity?'}))

    class Meta:
        model = FitnessActivity
        fields = ['activity_type', 'duration_minutes']