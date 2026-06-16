from datetime import timedelta

from django.db import models
from django.utils import timezone

from accounts.models import User


class DonorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='donor_profile'
    )
    last_donation_date = models.DateField(
        blank=True, null=True,
        help_text="تاريخ آخر تبرع — يُحدَّث تلقائياً بعد كل عملية"
    )
    total_donations = models.IntegerField(default=0)
    is_available = models.BooleanField(
        default=True,
        help_text="False = ضمن فترة الحظر الصحي (90 يوماً)"
    )

    def update_availability(self):
        """
        قاعدة صحية: لا يجوز التبرع قبل مرور 90 يوماً من آخر تبرع.
        تُستدعى تلقائياً من الـ Signal بعد كل تبرع مكتمل.
        """
        if self.last_donation_date:
            days_passed = timezone.now().date() - self.last_donation_date
            self.is_available = days_passed >= timedelta(days=90)
        else:
            self.is_available = True
        self.save(update_fields=['is_available'])

    def days_until_available(self):
        """تُعيد عدد الأيام المتبقية للمتبرع ليصبح مؤهلاً مجدداً."""
        if self.last_donation_date and not self.is_available:
            next_date = self.last_donation_date + timedelta(days=90)
            remaining = (next_date - timezone.now().date()).days
            return max(0, remaining)
        return 0

    def __str__(self):
        return f"ملف {self.user.get_full_name()} — التبرعات: {self.total_donations}"
