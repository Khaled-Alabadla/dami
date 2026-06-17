from blood_requests.compatibility import compatible_recipient_types
from blood_requests.models import BloodRequest


def urgent_requests(request):
    """
    Inject the count of urgent blood requests matching the current donor.

    Runs on every request for the navbar alert bar. Returns ``{'urgent_count': 0}``
    for anonymous users, non-donors, or donors inside their 90-day cooldown.
    """
    user = request.user
    if not (user.is_authenticated and user.role == 'donor' and user.blood_type and user.city_id):
        return {'urgent_count': 0}

    profile = getattr(user, 'donor_profile', None)
    if profile:
        profile.update_availability()
        if not profile.is_available:
            return {'urgent_count': 0}

    compatible = compatible_recipient_types(user.blood_type)
    count = BloodRequest.objects.filter(
        blood_type_needed__in=compatible,
        hospital__city=user.city,
        status='active',
    ).count()
    return {'urgent_count': count}
