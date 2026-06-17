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
    Render the donor's personalised dashboard.

    Shows only active blood requests that match both the donor's blood type
    (using the biological compatibility map) and their city. If the donor is
    within the 90-day cooldown window, the request grid is hidden entirely.

    Context variables injected into the template:
      - matching_requests:    QuerySet of compatible active BloodRequests
      - donor_profile:        The donor's DonorProfile instance
      - days_remaining:       Days left in the cooldown period (0 if eligible)
      - committed_ids:        Set of BloodRequest PKs with a 'going' record
      - completed_ids:        Set of BloodRequest PKs with a 'completed' record
      - donation_records:     Full donation history for the history table
      - has_going_commitment: True if the donor has any in-progress commitment
    """
    user = request.user
    profile = user.donor_profile
    profile.update_availability()

    if profile.is_available:
        compatible = compatible_recipient_types(user.blood_type)
        matching_requests = BloodRequest.objects.filter(
            blood_type_needed__in=compatible,
            hospital__city=user.city,
            status='active',
        ).select_related('hospital').order_by('-created_at')
    else:
        matching_requests = BloodRequest.objects.none()

    committed_ids = set(DonationRecord.objects.filter(
        donor=user,
        blood_request__in=matching_requests,
    ).values_list('blood_request_id', flat=True))

    completed_ids = set(DonationRecord.objects.filter(
        donor=user,
        blood_request__in=matching_requests,
        status='completed',
    ).values_list('blood_request_id', flat=True))

    donation_records = DonationRecord.objects.filter(
        donor=user,
    ).select_related('blood_request', 'blood_request__hospital').order_by('-donated_at')

    has_going_commitment = DonationRecord.objects.filter(
        donor=user, status='going',
    ).exists()

    context = {
        'matching_requests': matching_requests,
        'donor_profile': profile,
        'days_remaining': profile.days_until_available(),
        'committed_ids': committed_ids,
        'completed_ids': completed_ids,
        'donation_records': donation_records,
        'has_going_commitment': has_going_commitment,
    }
    return render(request, 'donors/dashboard.html', context)
