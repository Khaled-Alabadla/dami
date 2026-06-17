from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.email_service import send_email
from accounts.models import User
from .compatibility import compatible_donor_types
from .models import BloodRequest


@receiver(post_save, sender=BloodRequest)
def notify_donors_on_new_request(sender, instance, created, **kwargs):
    if not created or instance.status != 'active':
        return

    donor_types = compatible_donor_types(instance.blood_type_needed)
    if not donor_types:
        return

    donors = User.objects.filter(
        role='donor',
        blood_type__in=donor_types,
        city=instance.hospital.city,
        is_active=True,
    ).select_related('donor_profile')

    hospital_name = instance.hospital.get_full_name()
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
    dashboard_url = f'{site_url}/donor/dashboard/'

    for donor in donors:
        profile = donor.donor_profile
        profile.update_availability()
        if not profile.is_available:
            continue

        subject = f'🩸 حالة عاجلة — فصيلة {instance.blood_type_needed} في {instance.hospital.city}'
        html_body = (
            f'<p>مرحباً <strong>{donor.get_full_name()}</strong>،</p>'
            f'<p>يوجد طلب دم عاجل في <strong>{hospital_name}</strong> '
            f'يتطلب فصيلة <strong>{instance.blood_type_needed}</strong>.</p>'
            f'<p>📍 {instance.hospital_branch_address}</p>'
            f'<p>الأكياس المطلوبة: {instance.bags_required}</p>'
            f'<p><a href="{dashboard_url}">عرض الطلبات في لوحة المتبرع</a></p>'
            f'<p>— منصة دمي</p>'
        )
        send_email(donor.email, subject, html_body)
