from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from blood_requests.models import BloodRequest


@login_required
def request_list(request):
    if request.user.role == 'donor':
        donor_profile = request.user.donor_profile
        donor_profile.update_availability()
        if donor_profile.is_available:
            requests_qs = BloodRequest.objects.filter(
                blood_type_needed=request.user.blood_type,
                hospital__city=request.user.city,
                status='active',
            ).select_related('hospital')
        else:
            requests_qs = BloodRequest.objects.none()
    elif request.user.role == 'hospital':
        requests_qs = BloodRequest.objects.filter(
            hospital=request.user,
        ).select_related('hospital')
    else:
        requests_qs = BloodRequest.objects.all().select_related('hospital')

    requests_qs = requests_qs.order_by('-created_at')
    context = {'requests_list': requests_qs}

    if request.user.role == 'donor':
        from donations.models import DonationRecord
        context['committed_ids'] = set(
            DonationRecord.objects.filter(
                donor=request.user,
                blood_request__in=requests_qs,
            ).values_list('blood_request_id', flat=True)
        )

    return render(request, 'blood_requests/list.html', context)
