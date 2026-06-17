from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import DonationRecord


@receiver(pre_save, sender=DonationRecord)
def stash_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._prev_status = DonationRecord.objects.get(pk=instance.pk).status
        except DonationRecord.DoesNotExist:
            instance._prev_status = None
    else:
        instance._prev_status = None


@receiver(post_save, sender=DonationRecord)
def handle_donation_completed(sender, instance, **kwargs):
    """
    يُطلق فقط عند تأكيد المستشفى (status = completed).
    الالتزام بـ 'going' لا يُحدّث الأهلية ولا العداد.
    """
    if instance.status != 'completed':
        return
    if getattr(instance, '_prev_status', None) == 'completed':
        return

    profile = instance.donor.donor_profile
    profile.last_donation_date = timezone.now().date()
    profile.is_available = False
    profile.total_donations += 1
    profile.save(update_fields=[
        'last_donation_date', 'is_available', 'total_donations'
    ])

    blood_req = instance.blood_request
    from django.db.models import F
    blood_req.__class__.objects.filter(pk=blood_req.pk).update(
        bags_received=F('bags_received') + 1
    )
    blood_req.refresh_from_db()

    if blood_req.bags_received >= blood_req.bags_required:
        blood_req.status = 'fulfilled'
        blood_req.save(update_fields=['status'])
