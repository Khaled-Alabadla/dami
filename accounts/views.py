from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core import signing
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .email_service import send_verification_email, verify_verification_token
from .forms import DonorRegistrationForm, UserProfileForm, EmailAuthenticationForm
from .models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.role == 'donor':
            return reverse_lazy('donor_dashboard')
        if user.role == 'hospital':
            return reverse_lazy('hospital_dashboard')
        return reverse_lazy('admin:index')


def register_donor(request):
    if request.user.is_authenticated:
        return redirect('donor_dashboard')
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                phone_number=form.cleaned_data['phone_number'],
                city=form.cleaned_data['city'],
                blood_type=form.cleaned_data['blood_type'],
                role='donor',
                is_active=False,
            )
            send_verification_email(user, request)
            return redirect('verification_sent')
    else:
        form = DonorRegistrationForm()
    return render(request, 'accounts/register_donor.html', {'form': form})


def verification_sent(request):
    return render(request, 'accounts/verification_sent.html')


def verify_email(request, token):
    try:
        user_pk = verify_verification_token(token)
    except signing.SignatureExpired:
        messages.error(request, 'انتهت صلاحية رابط التفعيل (24 ساعة). يرجى التسجيل مجدداً.')
        return redirect('register_donor')
    except (signing.BadSignature, ValueError):
        messages.error(request, 'رابط التفعيل غير صالح.')
        return redirect('register_donor')

    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        messages.error(request, 'رابط التفعيل غير صالح.')
        return redirect('register_donor')

    if user.is_active:
        messages.info(request, 'تم تفعيل بريدك الإلكتروني مسبقاً. يمكنك تسجيل الدخول.')
        return redirect('login')

    user.is_active = True
    user.save(update_fields=['is_active'])
    messages.success(request, 'تم تأكيد بريدك الإلكتروني بنجاح! مرحباً بك في منصة دمي 🩸')
    return redirect('login')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات ملفك الشخصي بنجاح!')
            if request.user.role == 'donor':
                return redirect('donor_dashboard')
            elif request.user.role == 'hospital':
                return redirect('hospital_dashboard')
            return redirect('edit_profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {'form': form})
