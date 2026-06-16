from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.decorators import donor_required
from blood_requests.models import BloodRequest
from donations.models import DonationRecord


COMPATIBILITY_MAP = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],
}


@login_required
@donor_required
def donor_dashboard(request):
    """
    تعرض فقط الحالات العاجلة التي تطابق:
    - فصيلة دم المتبرع (بناءً على التوافق الحيوي)
    - مدينة المتبرع
    - حالة الطلب = active
    """
    user = request.user

    donor_profile = user.donor_profile
    donor_profile.update_availability()

    if donor_profile.is_available:
        compatible_recipients = COMPATIBILITY_MAP.get(user.blood_type, [])
        matching_requests = BloodRequest.objects.filter(
            blood_type_needed__in=compatible_recipients,
            hospital__city=user.city,
            status='active',
        ).select_related('hospital').order_by('-created_at')
    else:
        matching_requests = BloodRequest.objects.none()

    committed_ids = DonationRecord.objects.filter(
        donor=user,
        blood_request__in=matching_requests,
    ).values_list('blood_request_id', flat=True)

    completed_ids = set(DonationRecord.objects.filter(
        donor=user,
        blood_request__in=matching_requests,
        status='completed',
    ).values_list('blood_request_id', flat=True))

    context = {
        'matching_requests': matching_requests,
        'donor_profile': donor_profile,
        'days_remaining': donor_profile.days_until_available(),
        'committed_ids': set(committed_ids),
        'completed_ids': completed_ids,
    }
    return render(request, 'donors/dashboard.html', context)
