from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from .models import Event, EventApplication


# Home page
def home(request):
    return render(request, 'events/home.html')


# Events list page
def events_list(request):
    events = Event.objects.all().order_by('date')
    applied_event_ids = []

    # If the user is logged in, check which events they already applied for
    if request.user.is_authenticated:
        applied_event_ids = EventApplication.objects.filter(student=request.user).values_list('event_id', flat=True)

    return render(request, 'events/events_list.html', {
        'events': events,
        'applied_event_ids': applied_event_ids,
    })


# Event detail page
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


# Other static pages
def achievements(request):
    return render(request, 'events/achievements.html')

def gallery(request):
    return render(request, 'events/gallery.html')

def news(request):
    return render(request, 'events/news.html')

def about(request):
    return render(request, 'events/about.html')

def contact(request):
    return render(request, 'events/contact.html')



def apply_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)

        if user:
            already_applied = EventApplication.objects.filter(
                student=user, event=event
            ).exists()

            if not already_applied:
                EventApplication.objects.create(student=user, event=event)
                messages.success(request, "You have successfully applied!")
            else:
                messages.warning(request, "You have already applied for this event.")
        else:
            messages.error(request, "Incorrect password.")

    return redirect('events_list')