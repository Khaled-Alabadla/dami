from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='اسم المدينة')

    class Meta:
        verbose_name = 'مدينة'
        verbose_name_plural = 'المدن'
        ordering = ['name']

    def __str__(self):
        return self.name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""
        if not email:
            raise ValueError('يجب تقديم البريد الإلكتروني')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser, enforcing required flags."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        if not extra_fields['is_staff']:
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields['is_superuser']:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = (
        ('donor', 'متبرع بالدم'),
        ('hospital', 'مستشفى / بنك دم'),
        ('admin', 'مشرف المنصة'),
    )
    BLOOD_CHOICES = (
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    )

    username = None
    email = models.EmailField(unique=True, verbose_name='البريد الإلكتروني')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    phone_number = models.CharField(max_length=15, blank=True)
    city = models.ForeignKey(
        City, on_delete=models.PROTECT,
        related_name='users',
        verbose_name='المدينة',
        null=True, blank=True,
    )
    blood_type = models.CharField(
        max_length=5, choices=BLOOD_CHOICES,
        blank=True, null=True,
        help_text="مطلوب فقط للمتبرعين",
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        """Clear blood_type for non-donor roles to keep data consistent."""
        if self.role != 'donor':
            self.blood_type = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_full_name() or self.email
