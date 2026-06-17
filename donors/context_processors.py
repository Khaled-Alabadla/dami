from blood_requests.compatibility import compatible_recipient_types
from blood_requests.models import BloodRequest
from donors.models import DonorProfile


def urgent_requests(request):
    if (
        request.user.is_authenticated
        and request.user.role == 'donor'
        and request.user.blood_type
        and request.user.city_id
    ):
        try:
            profile = DonorProfile.objects.get(user=request.user)
            profile.update_availability()
            if not profile.is_available:
                return {'urgent_count': 0}
        except DonorProfile.DoesNotExist:
            pass

        compatible = compatible_recipient_types(request.user.blood_type)
        count = BloodRequest.objects.filter(
            blood_type_needed__in=compatible,
            hospital__city=request.user.city,
            status='active',
        ).count()
        return {'urgent_count': count}
    return {'urgent_count': 0}
