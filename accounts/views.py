from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import DonorRegistrationForm, UserProfileForm, EmailAuthenticationForm
from .models import User
from .otp import (
    generate_otp,
    send_otp_sms,
    store_otp_in_session,
    verify_otp_from_session,
    can_resend_otp,
)


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
            # حفظ بيانات التسجيل مؤقتاً في الـ Session
            request.session['pending_registration'] = {
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'phone_number': form.cleaned_data['phone_number'],
                'city_id': form.cleaned_data['city'].id,
                'blood_type': form.cleaned_data['blood_type'],
                'password': form.cleaned_data['password'],
            }
            # توليد وإرسال OTP
            phone = form.cleaned_data['phone_number']
            otp_code = generate_otp()
            store_otp_in_session(request, phone, otp_code)
            send_otp_sms(phone, otp_code)
            return redirect('verify_otp')
    else:
        form = DonorRegistrationForm()
    return render(request, 'accounts/register_donor.html', {'form': form})


def verify_otp(request):
    """صفحة إدخال رمز التحقق من الجوال."""
    # التحقق من وجود بيانات تسجيل معلّقة
    pending = request.session.get('pending_registration')
    otp_data = request.session.get('otp_data')
    if not pending or not otp_data:
        messages.error(request, 'انتهت صلاحية الجلسة. يرجى إعادة التسجيل.')
        return redirect('register_donor')

    # إخفاء رقم الجوال جزئياً (مثل: ****1234)
    phone = otp_data.get('phone', '')
    masked_phone = '*' * max(0, len(phone) - 4) + phone[-4:] if len(phone) >= 4 else phone

    error_message = None

    if request.method == 'POST':
        submitted_code = request.POST.get('otp_code', '')
        success, error_message = verify_otp_from_session(request, submitted_code)

        if success:
            # إنشاء المستخدم
            user = User.objects.create_user(
                email=pending['email'],
                password=pending['password'],
                first_name=pending['first_name'],
                last_name=pending['last_name'],
                phone_number=pending['phone_number'],
                city_id=pending['city_id'],
                blood_type=pending['blood_type'],
                role='donor',
            )
            # تنظيف الـ Session
            request.session.pop('pending_registration', None)
            request.session.pop('otp_data', None)
            # تسجيل الدخول
            login(request, user)
            messages.success(request, 'تم التحقق بنجاح! مرحباً بك في منصة دمي 🩸')
            return redirect('donor_dashboard')

    return render(request, 'accounts/verify_otp.html', {
        'masked_phone': masked_phone,
        'error_message': error_message,
    })


@require_POST
def resend_otp(request):
    """إعادة إرسال رمز التحقق مع حماية cooldown."""
    pending = request.session.get('pending_registration')
    if not pending:
        return JsonResponse({'success': False, 'message': 'انتهت صلاحية الجلسة.'}, status=400)

    allowed, seconds_left = can_resend_otp(request)
    if not allowed:
        return JsonResponse({
            'success': False,
            'message': f'يرجى الانتظار {seconds_left} ثانية قبل إعادة الإرسال.',
            'cooldown': seconds_left,
        }, status=429)

    phone = pending['phone_number']
    otp_code = generate_otp()
    store_otp_in_session(request, phone, otp_code)
    sent = send_otp_sms(phone, otp_code)

    if sent:
        return JsonResponse({'success': True, 'message': 'تم إرسال رمز جديد بنجاح.'})
    else:
        return JsonResponse({'success': False, 'message': 'فشل إرسال الرسالة. حاول لاحقاً.'}, status=500)


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
