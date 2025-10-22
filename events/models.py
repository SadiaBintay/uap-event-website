
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    CATEGORY_CHOICES = [
        ('WORKSHOP', 'Workshop'),
        ('COMPETITION', 'Competition'),
        ('FAIR', 'Fair'),
        ('SEMINAR', 'Seminar'),
        ('CONFERENCE', 'Conference'),
    ]

    name = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='COMPETITION')
    password_required = models.BooleanField(default=False)
    allow_teams = models.BooleanField(default=False)  # NEW: Whether event allows teams
    max_team_size = models.IntegerField(default=4)   # NEW: Maximum team members

    def __str__(self):
        return self.name

class Team(models.Model):  # NEW MODEL
    team_name = models.CharField(max_length=100)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    team_leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='led_teams')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.team_name} - {self.event.name}"

class TeamMember(models.Model):  # NEW MODEL
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['team', 'student']

    def __str__(self):
        return f"{self.student.username} - {self.team.team_name}"

class EventApplication(models.Model):
    APPLICATION_TYPES = [  # NEW: Added types
        ('INDIVIDUAL', 'Individual'),
        ('TEAM', 'Team'),
    ]

    application_type = models.CharField(max_length=20, choices=APPLICATION_TYPES, default='INDIVIDUAL')  # NEW
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # CHANGED: Made optional
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)  # NEW: For team applications
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.application_type == 'INDIVIDUAL':
            return f"{self.student.username} - {self.event.name}"
        else:
            return f"{self.team.team_name} - {self.event.name}"

class Winner(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='winners')
    winner_name = models.CharField(max_length=100)
    group_or_person = models.CharField(max_length=50, choices=[('Group', 'Group'), ('Person', 'Person')])
    position = models.CharField(max_length=20, choices=[('1st', '1st'), ('2nd', '2nd'), ('3rd', '3rd')])

    def __str__(self):
        return f"{self.winner_name} - {self.event.name}"

class GalleryItem(models.Model):
        MEDIA_TYPES = (
            ('image', 'Image'),
            ('video', 'Video'),
        )

        title = models.CharField(max_length=200)
        description = models.TextField(blank=True)
        media_type = models.CharField(max_length=5, choices=MEDIA_TYPES)
        file = models.FileField(upload_to='gallery/')
        uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
        uploaded_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.title