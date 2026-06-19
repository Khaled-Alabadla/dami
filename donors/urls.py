from django.urls import path

from .views import donor_dashboard, toggle_notifications

urlpatterns = [
    path('dashboard/', donor_dashboard, name='donor_dashboard'),
    path('notifications/toggle/', toggle_notifications, name='toggle_notifications'),
]
