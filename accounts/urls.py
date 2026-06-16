from django.urls import path

from .views import CustomLoginView, logout_view, register_donor, edit_profile, verify_otp, resend_otp

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/donor/', register_donor, name='register_donor'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    path('profile/', edit_profile, name='edit_profile'),
]
