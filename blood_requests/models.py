from django.db import models

from accounts.models import User


class BloodRequest(models.Model):
    STATUS_CHOICES = (
        ('active', 'عاجل / مستمر'),
        ('fulfilled', 'تم توفير الكمية'),
        ('closed', 'مغلق / ملغي'),
    )
    hospital = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='blood_requests',
        limit_choices_to={'role': 'hospital'}
    )
    patient_name_hidden = models.CharField(
        max_length=100,
        help_text="سري تماماً — لا يظهر في أي واجهة مواجهة للمتبرعين"
    )
    blood_type_needed = models.CharField(
        max_length=5, choices=User.BLOOD_CHOICES
    )
    bags_required = models.IntegerField(default=1)
    bags_received = models.IntegerField(default=0)
    hospital_branch_address = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def bags_remaining(self):
        return self.bags_required - self.bags_received

    @property
    def fulfillment_percentage(self):
        if self.bags_required == 0:
            return 100
        return int((self.bags_received / self.bags_required) * 100)

    def __str__(self):
        return f"طلب {self.blood_type_needed} — {self.hospital.city} ({self.status})"
