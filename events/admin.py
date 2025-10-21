
from django.contrib import admin
from .models import Event, EventApplication, Winner  # import all your models

from django.contrib import admin
from .models import Event, EventApplication, Winner, Team, TeamMember


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'date', 'location', 'allow_teams', 'max_team_size', 'password_required']
    list_filter = ['category', 'allow_teams', 'date', 'password_required']
    search_fields = ['name', 'description', 'location']
    list_editable = ['allow_teams', 'max_team_size']


@admin.register(EventApplication)
class EventApplicationAdmin(admin.ModelAdmin):
    list_display = ['get_applicant', 'event', 'application_type', 'applied_at']
    list_filter = ['application_type', 'event', 'applied_at']
    search_fields = ['student__username', 'team__team_name', 'event__name']

    def get_applicant(self, obj):
        if obj.application_type == 'INDIVIDUAL':
            return f"👤 {obj.student.username}"
        else:
            return f"👥 {obj.team.team_name}"

    get_applicant.short_description = 'Applicant'


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['team_name', 'event', 'team_leader', 'get_member_count', 'created_at']
    list_filter = ['event', 'created_at']
    search_fields = ['team_name', 'team_leader__username', 'event__name']

    def get_member_count(self, obj):
        return obj.members.count()

    get_member_count.short_description = 'Members'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ['team', 'student', 'joined_at']
    list_filter = ['team__event', 'joined_at']
    search_fields = ['team__team_name', 'student__username']


@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display = ['winner_name', 'event', 'position', 'group_or_person']
    list_filter = ['event', 'position', 'group_or_person']
    search_fields = ['winner_name', 'event__name']