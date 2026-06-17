from django.db import models

from accounts.models import User
from blood_requests.models import BloodRequest


class DonationRecord(models.Model):
    """
    Records a donor's commitment to (and outcome of) a specific BloodRequest.

    Lifecycle: going → completed | failed
      - 'going'     – donor is on their way; no eligibility changes yet.
      - 'completed' – hospital confirms the donation; triggers the post_save
                      signal that updates DonorProfile and bag counts.
      - 'failed'    – donor did not show up; no eligibility changes.
    """

    STATUS_CHOICES = [
        ('going', 'في الطريق إلى المستشفى'),
        ('completed', 'تم التبرع بنجاح'),
        ('failed', 'لم يتم التبرع'),
    ]

    blood_request = models.ForeignKey(
        BloodRequest, on_delete=models.CASCADE, related_name='donations',
    )
    donor = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='my_donations',
        limit_choices_to={'role': 'donor'},
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='going')
    donated_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(
        blank=True, null=True,
        help_text="يُملأ تلقائياً عند تأكيد المستشفى",
    )

    class Meta:
        unique_together = ('blood_request', 'donor')
        ordering = ['-donated_at']

    def __str__(self):
        return f"{self.donor.get_full_name()} → {self.blood_request}"
