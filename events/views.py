from django.shortcuts import render, get_object_or_404
from .models import Event

# Home page
def home(request):
    return render(request, 'events/home.html')

# Events list page (with news section)
def events_list(request):
    events = Event.objects.all().order_by('date')  # Fetch all events from DB ordered by date
    return render(request, 'events/events_list.html', {'events': events})

# Event detail page
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)  # If event doesn't exist, return 404
    return render(request, 'events/event_detail.html', {'event': event})

# Achievements page
def achievements(request):
    return render(request, 'events/achievements.html')

# Gallery page
def gallery(request):
    return render(request, 'events/gallery.html')

# News page
def news(request):
    return render(request, 'events/news.html')

# About page
def about(request):
    return render(request, 'events/about.html')

# Contact page
def contact(request):
    return render(request, 'events/contact.html')
