from django.urls import path

from .views import confirm_donation, create_blood_request, hospital_dashboard, delete_blood_request

urlpatterns = [
    path('dashboard/', hospital_dashboard, name='hospital_dashboard'),
    path('requests/create/', create_blood_request, name='create_blood_request'),
    path('confirm/<int:record_id>/', confirm_donation, name='confirm_donation'),
    path('requests/<int:request_id>/delete/', delete_blood_request, name='delete_blood_request'),
]
