import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

VERIFICATION_TOKEN_MAX_AGE = 60 * 60 * 24  # 24 hours


def generate_verification_token(user_pk: int) -> str:
    """
    Return a signed, timestamped token encoding the given user PK.

    The token is URL-safe and can later be validated with
    `verify_verification_token`. It expires after VERIFICATION_TOKEN_MAX_AGE
    seconds (default: 24 hours).
    """
    signer = signing.TimestampSigner(salt='email-verification')
    return signer.sign(str(user_pk))


def verify_verification_token(token: str) -> int:
    """
    Validate a verification token and return the encoded user PK.

    Raises:
        signing.SignatureExpired: Token is older than VERIFICATION_TOKEN_MAX_AGE.
        signing.BadSignature:     Token has been tampered with.
        ValueError:               Token payload cannot be cast to int.
    """
    signer = signing.TimestampSigner(salt='email-verification')
    value = signer.unsign(token, max_age=VERIFICATION_TOKEN_MAX_AGE)
    return int(value)


def send_verification_email(user, request=None) -> bool:
    """
    Send an email verification link to *user*.

    Builds an absolute URL for the verify_email view using *request* when
    available, otherwise falls back to settings.SITE_URL. Returns True on
    success or False on failure.
    """
    token = generate_verification_token(user.pk)

    if request is not None:
        verify_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token})
        )
    else:
        site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
        verify_url = f"{site_url}{reverse('verify_email', kwargs={'token': token})}"

    subject = 'تأكيد بريدك الإلكتروني — منصة دمي'
    html_body = f"""
<div dir="rtl" style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#fff8f8;border-radius:12px;border:1px solid #fde0e0;">
  <div style="text-align:center;margin-bottom:24px;">
    <h1 style="color:#c0392b;font-size:28px;margin:0;">🩸 منصة دمي</h1>
    <p style="color:#888;font-size:13px;margin:4px 0 0;">شبكة التبرع بالدم في غزة</p>
  </div>
  <h2 style="color:#333;font-size:20px;">مرحباً {user.get_full_name() or user.email}،</h2>
  <p style="color:#555;line-height:1.7;">
    شكراً لتسجيلك في منصة <strong>دمي</strong>. يرجى تأكيد بريدك الإلكتروني للبدء في إنقاذ الأرواح.
  </p>
  <div style="text-align:center;margin:32px 0;">
    <a href="{verify_url}"
       style="background:linear-gradient(135deg,#c0392b,#922b21);color:#fff;text-decoration:none;
              padding:14px 36px;border-radius:8px;font-weight:bold;font-size:16px;display:inline-block;">
      تأكيد البريد الإلكتروني
    </a>
  </div>
  <p style="color:#999;font-size:13px;line-height:1.6;">
    هذا الرابط صالح لمدة <strong>24 ساعة</strong>. إذا لم تقم بالتسجيل، يمكنك تجاهل هذه الرسالة.
  </p>
  <hr style="border:none;border-top:1px solid #fde0e0;margin:20px 0;" />
  <p style="color:#bbb;font-size:11px;text-align:center;">منصة دمي — غزة 🇵🇸</p>
</div>
"""
    return send_email(to=user.email, subject=subject, html_body=html_body)


def send_email(to: str, subject: str, html_body: str, text_body: str = None) -> bool:
    """
    Dispatch an email through Django's configured EMAIL_BACKEND.

    In development (no Gmail credentials in .env), the backend is
    console.EmailBackend and the message is printed to the terminal.
    In production (GMAIL_USER + GMAIL_APP_PASSWORD set), the backend is
    smtp.EmailBackend and the message is delivered via Gmail.

    Returns True on success, False on any exception.
    """
    text_body = text_body or _strip_html(html_body)
    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            html_message=html_body,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception('Failed to send email to %s', to)
        return False


def _strip_html(html: str) -> str:
    """Convert a simple HTML string to plain text for multipart emails."""
    return (
        html
        .replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        .replace('<p>', '').replace('</p>', '\n')
        .replace('<strong>', '').replace('</strong>', '')
    )
