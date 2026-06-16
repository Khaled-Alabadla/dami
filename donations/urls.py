from django.urls import path

from .views import commit_to_donate

urlpatterns = [
    path('commit/<int:request_id>/', commit_to_donate, name='commit_to_donate'),
]
