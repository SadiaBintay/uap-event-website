
from django.db import models
from django.contrib.auth.models import User
from events.models import Event

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('EVENT_REMINDER', 'Event Reminder'),
        ('APPLICATION_STATUS', 'Application Status'),
        ('TEAM_INVITATION', 'Team Invitation'),
        ('WINNER_ANNOUNCEMENT', 'Winner Announcement'),
        ('SYSTEM', 'System Notification'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Foreign Key 1
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    related_event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)  # Foreign Key 2
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    icon = models.ImageField(upload_to='notification_icons/', blank=True, null=True)  # Media usage

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Foreign Key 3
    email_notifications = models.BooleanField(default=True)
    event_reminders = models.BooleanField(default=True)
    application_updates = models.BooleanField(default=True)
    team_notifications = models.BooleanField(default=True)
    winner_announcements = models.BooleanField(default=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"