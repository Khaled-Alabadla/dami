from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def home(request):
    """Redirect each user to their own dashboard, or to login if unauthenticated."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == 'hospital':
        return redirect('hospital_dashboard')
    return redirect('donor_dashboard')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('donor/', include('donors.urls')),
    path('hospital/', include('hospitals.urls')),
    path('donate/', include('donations.urls')),
    path('requests/', include('blood_requests.urls')),
    path('', home, name='home'),
]
