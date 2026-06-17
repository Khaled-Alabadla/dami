from datetime import timedelta

from django.db import models
from django.utils import timezone

from accounts.models import User


class DonorProfile(models.Model):
    """Tracks donation history and eligibility for a single donor."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    last_donation_date = models.DateField(
        blank=True, null=True,
        help_text="تاريخ آخر تبرع — يُحدَّث تلقائياً بعد كل عملية",
    )
    total_donations = models.IntegerField(default=0)
    is_available = models.BooleanField(
        default=True,
        help_text="False = ضمن فترة الحظر الصحي (90 يوماً)",
    )

    def update_availability(self):
        """
        Recompute and persist the donor's eligibility status.

        A donor must wait 90 days after their last completed donation before
        they can donate again. Called automatically after each confirmed
        donation via the DonationRecord post_save signal.
        """
        if self.last_donation_date:
            elapsed = timezone.now().date() - self.last_donation_date
            self.is_available = elapsed >= timedelta(days=90)
        else:
            self.is_available = True
        self.save(update_fields=['is_available'])

    def days_until_available(self) -> int:
        """
        Return the number of days remaining until the donor is eligible again.

        Returns 0 if the donor is already eligible or has no donation history.
        """
        if self.last_donation_date and not self.is_available:
            next_eligible = self.last_donation_date + timedelta(days=90)
            return max(0, (next_eligible - timezone.now().date()).days)
        return 0

    def __str__(self):
        return f"ملف {self.user.get_full_name()} — التبرعات: {self.total_donations}"
