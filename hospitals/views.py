from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import hospital_required
from blood_requests.models import BloodRequest
from donations.models import DonationRecord
from .forms import BloodRequestForm


@login_required
@hospital_required
def hospital_dashboard(request):
    """
    Render the hospital's dashboard.

    Shows all blood requests created by this hospital and the full list of
    donation commitments across all of them, so staff can confirm arrivals.
    """
    blood_requests = BloodRequest.objects.filter(
        hospital=request.user,
    ).order_by('-created_at')

    donation_records = DonationRecord.objects.filter(
        blood_request__hospital=request.user,
    ).select_related('donor', 'blood_request').order_by('-donated_at')

    return render(request, 'hospitals/dashboard.html', {
        'blood_requests': blood_requests,
        'donation_records': donation_records,
    })


@login_required
@hospital_required
def create_blood_request(request):
    """Handle the form for creating a new BloodRequest for this hospital."""
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.hospital = request.user
            blood_request.hospital_branch_address = (
                request.user.city.name if request.user.city else 'غير محدد'
            )
            blood_request.save()
            return redirect('hospital_dashboard')
    else:
        form = BloodRequestForm()

    return render(request, 'hospitals/create_request.html', {'form': form})


@login_required
@hospital_required
@require_POST
def confirm_donation(request, record_id):
    """
    AJAX endpoint for lab staff to confirm that a donor arrived and donated.

    Sets the DonationRecord status to 'completed' and stamps confirmed_at.
    The post_save signal on DonationRecord then updates the donor's profile
    and the request's bags_received counter automatically.

    Returns JSON with the updated bag counts for the frontend to display.
    """
    record = get_object_or_404(
        DonationRecord.objects.select_related('donor', 'blood_request'),
        id=record_id,
        blood_request__hospital=request.user,
    )

    record.status = 'completed'
    record.confirmed_at = timezone.now()
    record.save()

    record.blood_request.refresh_from_db()

    return JsonResponse({
        'success': True,
        'message': 'شكراً لمساهمتك، ربما يكون تبرعك سبباً في إنقاذ نفس',
        'bags_received': record.blood_request.bags_received,
        'bags_required': record.blood_request.bags_required,
    })


@login_required
@hospital_required
@require_POST
def delete_blood_request(request, request_id):
    """
    AJAX endpoint for a hospital to delete one of its own BloodRequests.

    Uses get_object_or_404 scoped to the requesting hospital to prevent
    hospitals from deleting each other's requests.
    """
    blood_request = get_object_or_404(
        BloodRequest, id=request_id, hospital=request.user,
    )
    blood_request.delete()
    return JsonResponse({'success': True, 'message': 'تم حذف طلب التبرع بالدم بنجاح.'})
