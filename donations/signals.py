from django.db.models import F
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from blood_requests.models import BloodRequest
from .models import DonationRecord


@receiver(pre_save, sender=DonationRecord)
def stash_previous_status(sender, instance, **kwargs):
    """
    Cache the current database status on the instance before saving.

    This allows post_save to detect genuine status transitions (e.g.
    going → completed) without an extra query.
    """
    if instance.pk:
        try:
            instance._prev_status = DonationRecord.objects.values_list(
                'status', flat=True,
            ).get(pk=instance.pk)
        except DonationRecord.DoesNotExist:
            instance._prev_status = None
    else:
        instance._prev_status = None


@receiver(post_save, sender=DonationRecord)
def handle_donation_completed(sender, instance, **kwargs):
    """
    Update donor profile and request bag counts when a donation is confirmed.

    Triggered only when status transitions to 'completed' for the first time.
    Side effects:
      - Sets DonorProfile.last_donation_date to today and is_available=False.
      - Increments DonorProfile.total_donations.
      - Increments BloodRequest.bags_received via an atomic F() update.
      - Marks the BloodRequest as 'fulfilled' if all bags have been received.
    """
    if instance.status != 'completed':
        return
    if getattr(instance, '_prev_status', None) == 'completed':
        return

    profile = instance.donor.donor_profile
    profile.last_donation_date = timezone.now().date()
    profile.is_available = False
    profile.total_donations += 1
    profile.save(update_fields=['last_donation_date', 'is_available', 'total_donations'])

    BloodRequest.objects.filter(pk=instance.blood_request_id).update(
        bags_received=F('bags_received') + 1,
    )

    blood_req = instance.blood_request
    blood_req.refresh_from_db()
    if blood_req.bags_received >= blood_req.bags_required:
        blood_req.status = 'fulfilled'
        blood_req.save(update_fields=['status'])
