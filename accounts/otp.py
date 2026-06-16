"""
خدمة OTP — توليد وإرسال والتحقق من رموز التحقق عبر SMS.
يتم تخزين الرمز في الـ Session دون الحاجة لجدول في قاعدة البيانات.
"""
import random
import string
import time
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def generate_otp(length=None):
    """توليد رمز عشوائي رقمي."""
    length = length or getattr(settings, 'OTP_LENGTH', 6)
    return ''.join(random.choices(string.digits, k=length))


def send_otp_sms(phone_number, otp_code):
    """
    محاكاة إرسال رمز التحقق بطباعته في الـ Console والـ Log.
    يُرجع True دائماً كمحاكاة للنجاح.
    """
    logger.info(f'OTP sent to {phone_number[-4:]} (Console Mode): {otp_code}')
    print(f"\n========================================")
    print(f"[SMS Console] OTP for {phone_number}: {otp_code}")
    print(f"========================================\n")
    return True


def store_otp_in_session(request, phone_number, otp_code):
    """حفظ بيانات OTP في الـ Session."""
    request.session['otp_data'] = {
        'phone': phone_number,
        'code': otp_code,
        'created_at': time.time(),
        'attempts': 0,
    }


def verify_otp_from_session(request, submitted_code):
    """
    التحقق من الرمز المُدخل.
    يُرجع: (success: bool, error_message: str | None)
    """
    otp_data = request.session.get('otp_data')
    if not otp_data:
        return False, 'انتهت صلاحية الجلسة. يرجى إعادة التسجيل.'

    # التحقق من انتهاء الصلاحية
    expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 5)
    elapsed = time.time() - otp_data['created_at']
    if elapsed > expiry_minutes * 60:
        # تنظيف الـ Session
        request.session.pop('otp_data', None)
        request.session.pop('pending_registration', None)
        return False, 'انتهت صلاحية الرمز. يرجى إعادة التسجيل.'

    # حماية من محاولات التخمين (5 محاولات كحد أقصى)
    otp_data['attempts'] = otp_data.get('attempts', 0) + 1
    request.session['otp_data'] = otp_data
    if otp_data['attempts'] > 5:
        request.session.pop('otp_data', None)
        request.session.pop('pending_registration', None)
        return False, 'تم تجاوز الحد الأقصى للمحاولات. يرجى إعادة التسجيل.'

    # مقارنة الرمز
    if submitted_code.strip() != otp_data['code']:
        remaining = 5 - otp_data['attempts']
        return False, f'الرمز غير صحيح. لديك {remaining} محاولات متبقية.'

    return True, None


def can_resend_otp(request):
    """
    التحقق من إمكانية إعادة إرسال الرمز (cooldown).
    يُرجع: (can_resend: bool, seconds_remaining: int)
    """
    otp_data = request.session.get('otp_data')
    if not otp_data:
        return False, 0

    cooldown = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)
    elapsed = time.time() - otp_data['created_at']
    if elapsed < cooldown:
        return False, int(cooldown - elapsed)

    return True, 0
