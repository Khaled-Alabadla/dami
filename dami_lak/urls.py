from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import include, path


def home(request):
    """Redirect each user to their own dashboard, or to login if unauthenticated."""
    if not request.user.is_authenticated:
        return redirect('login')
    if request.user.role == 'hospital':
        return redirect('hospital_dashboard')
    return redirect('donor_dashboard')


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)


def permission_denied(request, exception=None):
    return render(request, '403.html', status=403)


# Registered at module level — Django picks these up from ROOT_URLCONF
handler404 = page_not_found
handler403 = permission_denied

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('donor/', include('donors.urls')),
    path('hospital/', include('hospitals.urls')),
    path('donate/', include('donations.urls')),
    path('requests/', include('blood_requests.urls')),
    path('', home, name='home'),
]

# ── Development-only preview URLs for error pages ──────────────────
# Visit /errors/404/ or /errors/403/ while DEBUG=True to preview them.
if settings.DEBUG:
    urlpatterns += [
        path('errors/404/', lambda r: render(r, '404.html', status=404)),
        path('errors/403/', lambda r: render(r, '403.html', status=403)),
    ]
