from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import User
from .models import DonorProfile


@receiver(post_save, sender=User)
def create_donor_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'donor':
        DonorProfile.objects.get_or_create(user=instance)
