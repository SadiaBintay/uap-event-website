from django import forms
from .models import NotificationPreference

class NotificationPreferenceForm(forms.ModelForm):
    class Meta:
        model = NotificationPreference
        fields = ['email_notifications', 'event_reminders', 'application_updates', 'team_notifications', 'winner_announcements']
        widgets = {
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'event_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'application_updates': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'team_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'winner_announcements': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }