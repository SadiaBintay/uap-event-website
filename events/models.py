# events/models.py
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    description = models.TextField()
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class EventApplication(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.student.username} - {self.event.name}"
