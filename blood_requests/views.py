from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from blood_requests.compatibility import compatible_recipient_types
from blood_requests.models import BloodRequest
from donations.models import DonationRecord


@login_required
def request_list(request):
    user = request.user

    if user.role == 'donor':
        profile = user.donor_profile
        profile.update_availability()
        
        compatible = compatible_recipient_types(user.blood_type)
        requests_qs = BloodRequest.objects.filter(
            blood_type_needed__in=compatible,
            hospital__city=user.city,
            status='active',
        ).select_related('hospital')
        
    elif user.role == 'hospital':
        requests_qs = BloodRequest.objects.filter(
            hospital=user,
        ).select_related('hospital')
    else:
        requests_qs = BloodRequest.objects.all().select_related('hospital')

    requests_qs = requests_qs.order_by('-created_at')
    context = {'requests_list': requests_qs}

    if user.role == 'donor':
        context['is_donor_available'] = profile.is_available

        context['committed_ids'] = set(DonationRecord.objects.filter(
            donor=user,
            blood_request__in=requests_qs,
        ).values_list('blood_request_id', flat=True))

        context['completed_ids'] = set(DonationRecord.objects.filter(
            donor=user,
            status='completed',
        ).values_list('blood_request_id', flat=True))

        context['has_going_commitment'] = DonationRecord.objects.filter(
            donor=user, status='going',
        ).exists()

    return render(request, 'blood_requests/list.html', context)