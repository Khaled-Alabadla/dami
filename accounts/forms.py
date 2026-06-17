from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import City, User


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that accepts an email address instead of a username."""

    username = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={'autofocus': True}),
    )

    def confirm_login_allowed(self, user):
        """Raise a user-friendly error when the account is not yet verified."""
        if not user.is_active:
            raise ValidationError(
                'لم يتم تفعيل هذا الحساب بعد. '
                'يرجى التحقق من بريدك الإلكتروني والضغط على رابط التفعيل.',
                code='inactive',
            )


class DonorRegistrationForm(forms.ModelForm):
    """Registration form for new blood donors."""

    email = forms.EmailField(label='البريد الإلكتروني')
    first_name = forms.CharField(label='الاسم الأول', max_length=150)
    last_name = forms.CharField(label='اسم العائلة', max_length=150)
    phone_number = forms.CharField(label='رقم الهاتف', max_length=15)
    city = forms.ModelChoiceField(
        label='المدينة',
        queryset=City.objects.all(),
        empty_label='— اختر المدينة —',
    )
    blood_type = forms.ChoiceField(label='فصيلة الدم', choices=User.BLOOD_CHOICES)
    password = forms.CharField(label='كلمة المرور', widget=forms.PasswordInput())
    password_confirm = forms.CharField(label='تأكيد كلمة المرور', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'blood_type')

    def clean(self):
        """Validate that both password fields match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'كلمتا المرور غير متطابقتين.')
        return cleaned_data

    def save(self, commit=True):
        """Hash the password before saving."""
        user = super().save(commit=False)
        user.role = 'donor'
        user.blood_type = self.cleaned_data['blood_type']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Profile edit form; hides blood_type for non-donor accounts."""

    first_name = forms.CharField(label='الاسم الأول', max_length=150)
    last_name = forms.CharField(label='اسم العائلة', max_length=150, required=False)
    phone_number = forms.CharField(label='رقم الهاتف', max_length=15)
    city = forms.ModelChoiceField(
        label='المدينة',
        queryset=City.objects.all(),
        empty_label='— اختر المدينة —',
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'city', 'blood_type')
        labels = {
            'email': 'البريد الإلكتروني',
            'blood_type': 'فصيلة الدم',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.role != 'donor':
            self.fields.pop('blood_type', None)
