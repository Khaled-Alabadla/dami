from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from accounts.decorators import donor_required
from blood_requests.models import BloodRequest
from .models import DonationRecord


@login_required
@donor_required
@require_POST
def commit_to_donate(request, request_id):
    """
    يستقبل طلب AJAX عند ضغط المتبرع على 'أنا قادم'.
    يتحقق من الأهلية الصحية ثم يسجل الالتزام.
    """
    user = request.user
    profile = user.donor_profile
    profile.update_availability()

    if not profile.is_available:
        next_date = profile.last_donation_date
        allowed_date = next_date + timedelta(days=90)
        return JsonResponse({
            'success': False,
            'error': 'غير مؤهل صحياً حالياً',
            'allowed_from': allowed_date.strftime('%Y-%m-%d'),
            'days_remaining': profile.days_until_available(),
        }, status=403)

    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        status='active',
        blood_type_needed=user.blood_type,
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
