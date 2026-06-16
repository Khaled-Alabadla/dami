from django.contrib import admin

from .models import DonationRecord


@admin.register(DonationRecord)
class DonationRecordAdmin(admin.ModelAdmin):
    list_display = ('donor', 'blood_request', 'status', 'donated_at', 'confirmed_at')
    list_filter = ('status',)
    search_fields = ('donor__email', 'donor__first_name', 'blood_request__hospital__email', 'blood_request__hospital__first_name')
