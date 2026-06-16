from django.contrib import admin

from .models import BloodRequest


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = (
        'blood_type_needed', 'hospital', 'bags_required',
        'bags_received', 'status', 'created_at',
    )
    list_filter = ('status', 'blood_type_needed', 'hospital__city')
    search_fields = ('hospital__email', 'hospital__first_name', 'hospital_branch_address')
    readonly_fields = ('created_at', 'updated_at')
