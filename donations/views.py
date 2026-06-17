from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from accounts.decorators import donor_required
from blood_requests.compatibility import compatible_recipient_types
from blood_requests.models import BloodRequest
from .models import DonationRecord


@login_required
@donor_required
@require_POST
def commit_to_donate(request, request_id):
    """
    AJAX endpoint called when a donor clicks 'I'm coming to donate'.

    Checks (in order):
      1. Donor is within the 90-day eligibility window.
      2. Donor has no other in-progress ('going') commitment — one at a time.
      3. The requested BloodRequest exists, is active, and matches the donor's
         blood type and city.

    Returns JSON with ``success: true`` and the new record ID on success, or
    ``success: false`` with a descriptive ``error`` field on any failure.
    """
    user = request.user
    profile = user.donor_profile
    profile.update_availability()

    if not profile.is_available:
        return JsonResponse({
            'success': False,
            'error': 'غير مؤهل صحياً حالياً',
            'days_remaining': profile.days_until_available(),
        }, status=403)

    existing_going = DonationRecord.objects.filter(donor=user, status='going').first()
    if existing_going:
        return JsonResponse({
            'success': False,
            'already_committed_elsewhere': True,
            'error': 'لديك التزام قائم بحالة أخرى. يُرجى إتمام التزامك الحالي أولاً.',
        }, status=400)

    compatible = compatible_recipient_types(user.blood_type)
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        status='active',
        blood_type_needed__in=compatible,
        hospital__city=user.city,
    )

    record, created = DonationRecord.objects.get_or_create(
        blood_request=blood_request,
        donor=user,
        defaults={'status': 'going'},
    )

    if not created:
        return JsonResponse({
            'success': False,
            'error': 'أنت مسجل مسبقاً في هذه الحالة',
        }, status=400)

    return JsonResponse({
        'success': True,
        'message': 'تم تسجيل التزامك. شكراً لك!',
        'record_id': record.id,
    })
