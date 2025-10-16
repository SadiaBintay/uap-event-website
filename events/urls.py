from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.events_list, name='events_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('achievements/', views.achievements, name='achievements'),
    path('gallery/', views.gallery, name='gallery'),
    path('news/', views.news, name='news'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('events/apply/<int:event_id>/', views.apply_event, name='apply_event'),

]

