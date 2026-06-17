from django.urls import path

from .views import CustomLoginView, logout_view, register_donor, edit_profile, verification_sent, verify_email

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/donor/', register_donor, name='register_donor'),
    path('profile/', edit_profile, name='edit_profile'),
    path('verify/sent/', verification_sent, name='verification_sent'),
    path('verify/<token>/', verify_email, name='verify_email'),
]
