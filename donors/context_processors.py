from blood_requests.models import BloodRequest
from donors.models import DonorProfile


def urgent_requests(request):
    if (
        request.user.is_authenticated
        and request.user.role == 'donor'
        and request.user.blood_type
    ):
        try:
            profile = DonorProfile.objects.get(user=request.user)
            if not profile.is_available:
                return {'urgent_count': 0}
        except DonorProfile.DoesNotExist:
            pass
        count = BloodRequest.objects.filter(
            blood_type_needed=request.user.blood_type,
            hospital__city=request.user.city,
            status='active',
        ).count()
        return {'urgent_count': count}
    return {'urgent_count': 0}
