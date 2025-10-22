from django.shortcuts import  get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate
from django.db.models import Count, Q
from .models import Event, EventApplication, Winner, Team, TeamMember
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GalleryItem
from .forms import GalleryItemForm



def home(request):
    return render(request, 'events/home.html')


def events_list(request):
    # Group events by category
    categories_with_events = {}

    for category_value, category_name in Event.CATEGORY_CHOICES:
        events = Event.objects.filter(category=category_value).order_by('date')
        if events.exists():
            categories_with_events[category_name] = {
                'events': events,
                'description': get_category_description(category_name)
            }

    applied_event_ids = []
    team_applied_event_ids = []

    if request.user.is_authenticated:
        # Individual applications
        applied_event_ids = EventApplication.objects.filter(
            student=request.user
        ).values_list('event_id', flat=True)

        # Team applications (where user is team leader or member)
        team_applied_event_ids = EventApplication.objects.filter(
            Q(team__team_leader=request.user) |
            Q(team__members__student=request.user)
        ).values_list('event_id', flat=True)

    return render(request, 'events/events_list.html', {
        'categories_with_events': categories_with_events,
        'applied_event_ids': applied_event_ids,
        'team_applied_event_ids': team_applied_event_ids,
    })


def get_category_description(category_name):
    descriptions = {
        'Workshop': 'Hands-on sessions to learn new skills.',
        'Competition': 'A challenging contest to test skills and knowledge.',
        'Fair': 'Gatherings to explore, network, and discover opportunities.',
        'Seminar': 'Educational sessions with expert speakers.',
        'Conference': 'Large-scale meetings for knowledge sharing.'
    }
    return descriptions.get(category_name, 'Various events and activities.')


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'events/event_detail.html', {'event': event})


@login_required
def apply_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        # Check if password is required for this event
        if event.password_required:
            password = request.POST.get('password')
            user = authenticate(username=request.user.username, password=password)

            if not user:
                messages.error(request, "Incorrect password.")
                return redirect('events_list')
        else:
            user = request.user

        application_type = request.POST.get('application_type', 'individual')

        if application_type == 'individual':
            # INDIVIDUAL APPLICATION (existing logic)
            already_applied_individual = EventApplication.objects.filter(
                student=user, event=event
            ).exists()

            # Check if user is already in a team for this event
            already_in_team = EventApplication.objects.filter(
                event=event,
                team__members__student=user
            ).exists()

            if already_applied_individual:
                messages.warning(request, "You have already applied individually for this event.")
            elif already_in_team:
                messages.warning(request, "You are already part of a team for this event.")
            else:
                EventApplication.objects.create(
                    application_type='INDIVIDUAL',
                    student=user,
                    event=event
                )
                messages.success(request, f"You have successfully applied for {event.name}!")

        elif application_type == 'team' and event.allow_teams:
            # TEAM APPLICATION
            team_name = request.POST.get('team_name', '').strip()
            member_usernames_text = request.POST.get('team_members', '').strip()

            if not team_name:
                messages.error(request, "Please provide a team name.")
                return redirect('events_list')

            # Convert textarea to list of usernames
            member_usernames = [username.strip() for username in member_usernames_text.split('\n') if username.strip()]

            # Validate team size (including team leader)
            if len(member_usernames) + 1 > event.max_team_size:
                messages.error(request, f"Team size cannot exceed {event.max_team_size} members.")
                return redirect('events_list')

            # Check if team name already exists for this event
            if Team.objects.filter(team_name=team_name, event=event).exists():
                messages.error(request, f"Team name '{team_name}' is already taken for this event.")
                return redirect('events_list')

            # Check if team leader already applied
            leader_already_applied = EventApplication.objects.filter(
                Q(student=user, event=event) |
                Q(team__team_leader=user, event=event) |
                Q(team__members__student=user, event=event)
            ).exists()

            if leader_already_applied:
                messages.error(request, "You have already applied for this event (individually or with another team).")
                return redirect('events_list')

            # Create team
            team = Team.objects.create(
                team_name=team_name,
                event=event,
                team_leader=user
            )

            # Add team members (excluding empty lines and team leader)
            members_added = 0
            for username in member_usernames:
                if username != user.username:  # Skip team leader
                    try:
                        member_user = User.objects.get(username=username)

                        # Check if member already applied
                        member_already_applied = EventApplication.objects.filter(
                            Q(student=member_user, event=event) |
                            Q(team__team_leader=member_user, event=event) |
                            Q(team__members__student=member_user, event=event)
                        ).exists()

                        if member_already_applied:
                            messages.warning(request, f"User '{username}' has already applied for this event.")
                        else:
                            TeamMember.objects.create(team=team, student=member_user)
                            members_added += 1
                    except User.DoesNotExist:
                        messages.warning(request, f"User '{username}' not found.")

            # Create team application
            EventApplication.objects.create(
                application_type='TEAM',
                team=team,
                event=event
            )

            messages.success(request,
                             f"Team '{team_name}' with {members_added + 1} members successfully applied for {event.name}!")

        else:
            messages.error(request, "Team applications are not allowed for this event.")

    return redirect('events_list')


def achievements(request):
    # Get all winners ordered by event date (newest first)
    winners = Winner.objects.select_related('event').order_by('-event__date')

    # Top participants by number of events applied to (individual + team)
    top_participants = User.objects.annotate(
        individual_apps=Count('eventapplication'),
        team_apps=Count('teammember'),
        total_apps=Count('eventapplication') + Count('teammember')
    ).filter(Q(individual_apps__gt=0) | Q(team_apps__gt=0)).order_by('-total_apps')[:10]

    # Event statistics
    total_events = Event.objects.count()
    total_individual_applications = EventApplication.objects.filter(application_type='INDIVIDUAL').count()
    total_team_applications = EventApplication.objects.filter(application_type='TEAM').count()
    total_participations = total_individual_applications + total_team_applications

    # Count unique participants (individuals + team members)
    individual_participants = EventApplication.objects.filter(application_type='INDIVIDUAL').values(
        'student').distinct().count()
    team_participants = TeamMember.objects.values('student').distinct().count()
    unique_participants = individual_participants + team_participants

    # Group winners by event
    winners_by_event = {}
    for winner in winners:
        if winner.event.name not in winners_by_event:
            winners_by_event[winner.event.name] = []
        winners_by_event[winner.event.name].append(winner)

    # User-specific achievements (if logged in)
    user_achievements = {}
    if request.user.is_authenticated:
        user_individual_apps = EventApplication.objects.filter(
            student=request.user,
            application_type='INDIVIDUAL'
        ).count()

        user_team_apps = TeamMember.objects.filter(student=request.user).count()
        user_led_teams = Team.objects.filter(team_leader=request.user).count()

        user_total_apps = user_individual_apps + user_team_apps

        user_wins = Winner.objects.filter(
            Q(winner_name=request.user.get_full_name()) |
            Q(winner_name=request.user.username)
        ).count()

        user_achievements = {
            'individual_apps': user_individual_apps,
            'team_apps': user_team_apps,
            'led_teams': user_led_teams,
            'total_apps': user_total_apps,
            'wins': user_wins,
            'participation_rate': round((user_total_apps / total_events * 100), 2) if total_events > 0 else 0,
            'rank': None
        }

        # Calculate user's rank
        if user_total_apps > 0:
            user_rank = User.objects.annotate(
                individual_apps=Count('eventapplication'),
                team_apps=Count('teammember'),
                total_apps=Count('eventapplication') + Count('teammember')
            ).filter(total_apps__gt=user_total_apps).count() + 1
            user_achievements['rank'] = user_rank

    context = {
        'winners': winners,
        'winners_by_event': winners_by_event,
        'top_participants': top_participants,
        'total_events': total_events,
        'total_participations': total_participations,
        'unique_participants': unique_participants,
        'user_achievements': user_achievements,
    }

    return render(request, 'events/achievements.html', context)




def gallery(request):
    form = GalleryItemForm()
    items = GalleryItem.objects.all().order_by('-uploaded_at')  # newest first

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')  # or show a message
        form = GalleryItemForm(request.POST, request.FILES)
        if form.is_valid():
            gallery_item = form.save(commit=False)
            gallery_item.uploaded_by = request.user
            gallery_item.save()
            return redirect('gallery')  # redirect to same page

    context = {
        'items': items,
        'form': form
    }

    return render(request, 'events/gallery.html', context )


def news(request):
    return render(request, 'events/news.html')


def about(request):
    return render(request, 'events/about.html')


def contact(request):
    return render(request, 'events/contact.html')