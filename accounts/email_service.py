import logging

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.core import signing
from django.urls import reverse

logger = logging.getLogger(__name__)

VERIFICATION_TOKEN_MAX_AGE = 60 * 60 * 24  # 24 hours


def generate_verification_token(user_pk: int) -> str:
    signer = signing.TimestampSigner(salt='email-verification')
    return signer.sign(str(user_pk))


def verify_verification_token(token: str):
    """Returns user pk (int) on success, raises signing.BadSignature / signing.SignatureExpired on failure."""
    signer = signing.TimestampSigner(salt='email-verification')
    value = signer.unsign(token, max_age=VERIFICATION_TOKEN_MAX_AGE)
    return int(value)


def send_verification_email(user, request=None) -> bool:
    token = generate_verification_token(user.pk)

    if request is not None:
        verify_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token})
        )
    else:
        verify_url = f"{getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}{reverse('verify_email', kwargs={'token': token})}"

    subject = 'تأكيد بريدك الإلكتروني — منصة دمي'
    html_body = f"""
<div dir="rtl" style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #fff8f8; border-radius: 12px; border: 1px solid #fde0e0;">
  <div style="text-align: center; margin-bottom: 24px;">
    <h1 style="color: #c0392b; font-size: 28px; margin: 0;">🩸 منصة دمي</h1>
    <p style="color: #888; font-size: 13px; margin: 4px 0 0;">شبكة التبرع بالدم في غزة</p>
  </div>
  <h2 style="color: #333; font-size: 20px;">مرحباً {user.get_full_name() or user.email}،</h2>
  <p style="color: #555; line-height: 1.7;">
    شكراً لتسجيلك في منصة <strong>دمي</strong>. يرجى تأكيد بريدك الإلكتروني للبدء في إنقاذ الأرواح.
  </p>
  <div style="text-align: center; margin: 32px 0;">
    <a href="{verify_url}"
       style="background: linear-gradient(135deg, #c0392b, #922b21); color: #fff; text-decoration: none;
              padding: 14px 36px; border-radius: 8px; font-weight: bold; font-size: 16px; display: inline-block;">
      تأكيد البريد الإلكتروني
    </a>
  </div>
  <p style="color: #999; font-size: 13px; line-height: 1.6;">
    هذا الرابط صالح لمدة <strong>24 ساعة</strong>. إذا لم تقم بالتسجيل، يمكنك تجاهل هذه الرسالة.
  </p>
  <hr style="border: none; border-top: 1px solid #fde0e0; margin: 20px 0;" />
  <p style="color: #bbb; font-size: 11px; text-align: center;">منصة دمي — غزة 🇵🇸</p>
</div>
"""
    return send_email(to=user.email, subject=subject, html_body=html_body)


def send_email(to, subject, html_body, text_body=None):
    """
    إرسال بريد إلكتروني عبر Resend API أو Django mail backend.

    Priority:
      1. RESEND_API_KEY set → send via Resend (works in DEBUG too)
      2. No key + DEBUG=True  → print to console (development)
      3. No key + DEBUG=False → send via Django EMAIL_BACKEND (SMTP)
    """
    text_body = text_body or _strip_html(html_body)

    api_key = getattr(settings, 'EMAIL_API_KEY', '')
    if api_key:
        return _send_via_api(to, subject, html_body, text_body)

    if settings.DEBUG:
        print('\n' + '=' * 50)
        print(f'[Email — console fallback]')
        print(f'To      : {to}')
        print(f'Subject : {subject}')
        print('-' * 50)
        print(text_body)
        print('=' * 50 + '\n')
        return True

    return bool(send_mail(
        subject=subject,
        message=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        html_message=html_body,
        fail_silently=False,
    ))


def _send_via_api(to, subject, html_body, text_body):
    response = requests.post(
        settings.EMAIL_API_URL,
        headers={
            'Authorization': f'Bearer {settings.EMAIL_API_KEY}',
            'Content-Type': 'application/json',
        },
        json={
            'from': settings.DEFAULT_FROM_EMAIL,
            'to': [to],
            'subject': subject,
            'html': html_body,
            'text': text_body,
        },
        timeout=15,
    )
    if not response.ok:
        logger.error(
            'Email API error %s: %s',
            response.status_code,
            response.text,
        )
    return response.ok


def _strip_html(html):
    return (
        html.replace('<br>', '\n')
        .replace('<br/>', '\n')
        .replace('<br />', '\n')
        .replace('<p>', '')
        .replace('</p>', '\n')
        .replace('<strong>', '')
        .replace('</strong>', '')
    )
