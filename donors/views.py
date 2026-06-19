from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import donor_required
from blood_requests.compatibility import compatible_recipient_types
from blood_requests.models import BloodRequest
from donations.models import DonationRecord


@login_required
@donor_required
def donor_dashboard(request):
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


@require_POST
@login_required
@donor_required
def toggle_notifications(request):
    """
    Toggle the donor's email_notifications preference on or off.

    Reads the 'enabled' checkbox from the submitted form. A missing field
    (unchecked checkbox) means the user wants notifications off.
    Redirects back to the profile edit page after saving.
    """
    profile = request.user.donor_profile
    profile.email_notifications = request.POST.get('enabled') == 'on'
    profile.save(update_fields=['email_notifications'])
    if profile.email_notifications:
        messages.success(request, 'تم تفعيل إشعارات البريد الإلكتروني.')
    else:
        messages.info(request, 'تم إيقاف إشعارات البريد الإلكتروني.')
    return redirect('edit_profile')
