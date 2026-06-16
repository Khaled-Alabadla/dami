from django.contrib import admin

from .models import DonorProfile


@admin.register(DonorProfile)
class DonorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_donations', 'is_available', 'last_donation_date')
    list_filter = ('is_available',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
