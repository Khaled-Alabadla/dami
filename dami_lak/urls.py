from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('donor/', include('donors.urls')),
    path('hospital/', include('hospitals.urls')),
    path('donate/', include('donations.urls')),
    path('requests/', include('blood_requests.urls')),
    path('', RedirectView.as_view(url='/donor/dashboard/', permanent=False)),
]
