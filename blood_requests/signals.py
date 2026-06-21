import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.email_service import send_urgent_request_email
from accounts.models import User
from .compatibility import compatible_donor_types
from .models import BloodRequest

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BloodRequest)
def notify_donors_on_new_request(sender, instance, created, **kwargs):
    """
    Email eligible donors when a new active BloodRequest is created.

    Finds all donors whose blood type is compatible with the requested type
    and who live in the same city. Skips donors inside their 90-day cooldown.
    """
    if not created or instance.status != 'active':
        return

    donor_types = compatible_donor_types(instance.blood_type_needed)
    if not donor_types:
        logger.warning('notify_donors: no compatible donor types for %s', instance.blood_type_needed)
        return

    donors = User.objects.filter(
        role='donor',
        blood_type__in=donor_types,
        city=instance.hospital.city,
        is_active=True,
        donor_profile__email_notifications=True,
    ).select_related('donor_profile')

    logger.info(
        'notify_donors: request #%s (%s in %s) → %d candidate donor(s)',
        instance.pk, instance.blood_type_needed, instance.hospital.city, donors.count(),
    )

    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    dashboard_url = f'{site_url}/donor/dashboard/'
    profile_url   = f'{site_url}/accounts/profile/'

    sent = skipped = 0
    for donor in donors:
        profile = donor.donor_profile
        profile.update_availability()
        if not profile.is_available:
            logger.info('notify_donors: skip %s (cooldown)', donor.email)
            skipped += 1
            continue

        ok = send_urgent_request_email(donor, instance, dashboard_url, profile_url)
        if ok:
            sent += 1
            logger.info('notify_donors: email sent → %s', donor.email)
        else:
            logger.error('notify_donors: FAILED to send email → %s', donor.email)

    logger.info('notify_donors: done — sent=%d skipped=%d', sent, skipped)
