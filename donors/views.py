from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.decorators import donor_required
from blood_requests.compatibility import compatible_recipient_types
from blood_requests.models import BloodRequest
from donations.models import DonationRecord


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
        compatible_recipients = compatible_recipient_types(user.blood_type)
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

    donation_records = DonationRecord.objects.filter(
        donor=user,
    ).select_related('blood_request', 'blood_request__hospital').order_by('-donated_at')

    has_going_commitment = DonationRecord.objects.filter(
        donor=user,
        status='going',
    ).exists()

    context = {
        'matching_requests': matching_requests,
        'donor_profile': donor_profile,
        'days_remaining': donor_profile.days_until_available(),
        'committed_ids': set(committed_ids),
        'completed_ids': completed_ids,
        'donation_records': donation_records,
        'has_going_commitment': has_going_commitment,
    }
    return render(request, 'donors/dashboard.html', context)
