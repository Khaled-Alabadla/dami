import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

VERIFICATION_TOKEN_MAX_AGE = 60 * 60 * 24  # 24 hours

# ── Brand colours ────────────────────────────────────────────────────────────
_RED       = '#c0392b'
_RED_DARK  = '#922b21'
_RED_LIGHT = '#fdf2f2'
_GRAY_BG   = '#f0f2f5'
_TEXT      = '#1a1a2e'
_MUTED     = '#64748b'
_BORDER    = '#e2e8f0'
_WHITE     = '#ffffff'


# ─────────────────────────────────────────────────────────────────────────────
# Token helpers
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Email template builder
# ─────────────────────────────────────────────────────────────────────────────

def _build_email_html(
    greeting: str,
    body_html: str,
    cta_text: str,
    cta_url: str,
    footer_note: str = '',
) -> str:
    footer_note_html = (
        f'<p style="margin:24px 0 0;font-size:13px;color:{_MUTED};'
        f'line-height:1.7;border-right:3px solid {_BORDER};'
        f'padding-right:12px;">{footer_note}</p>'
        if footer_note else ''
    )

    return f"""\
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>منصة دمي</title>
</head>
<body style="margin:0;padding:0;background-color:{_GRAY_BG};
             font-family:'Segoe UI',Tahoma,'Helvetica Neue',Arial,sans-serif;">

  <!-- Outer wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0"
         style="background-color:{_GRAY_BG};padding:48px 16px;">
    <tr>
      <td align="center">

        <!-- Card -->
        <table width="600" cellpadding="0" cellspacing="0" border="0"
               style="max-width:600px;width:100%;background:{_WHITE};
                      border-radius:12px;overflow:hidden;
                      border:1px solid {_BORDER};
                      box-shadow:0 2px 16px rgba(0,0,0,0.06);">

          <!-- ── Top accent bar ───────────────────────────────────────── -->
          <tr>
            <td height="5" bgcolor="{_RED}"
                style="background:{_RED};font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- ── Header ───────────────────────────────────────────────── -->
          <tr>
            <td align="right" bgcolor="{_WHITE}"
                style="background:{_WHITE};padding:32px 40px 24px;">
              <table cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <span style="font-size:26px;font-weight:800;
                                 color:{_RED};letter-spacing:-0.5px;">
                      دمي
                    </span>
                    <span style="font-size:13px;color:{_MUTED};
                                 padding-right:10px;border-right:2px solid {_BORDER};
                                 margin-right:10px;">
                      منصة التبرع بالدم
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── Divider ──────────────────────────────────────────────── -->
          <tr>
            <td style="padding:0 40px;">
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td style="border-top:1px solid {_BORDER};"></td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── Body ─────────────────────────────────────────────────── -->
          <tr>
            <td style="padding:36px 40px 32px;direction:rtl;text-align:right;">

              <!-- Greeting -->
              <p style="margin:0 0 16px;font-size:18px;font-weight:700;
                        color:{_TEXT};line-height:1.4;">
                {greeting}
              </p>

              <!-- Body content -->
              <div style="font-size:15px;line-height:1.85;color:#475569;">
                {body_html}
              </div>

              <!-- CTA button -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin:32px 0 28px;">
                <tr>
                  <td align="right">
                    <a href="{cta_url}"
                       style="display:inline-block;background-color:{_RED};
                              color:{_WHITE};text-decoration:none;
                              font-size:15px;font-weight:700;
                              padding:14px 40px;border-radius:8px;
                              letter-spacing:0.2px;">
                      {cta_text}
                    </a>
                  </td>
                </tr>
              </table>

              {footer_note_html}

            </td>
          </tr>

          <!-- ── Footer ────────────────────────────────────────────────── -->
          <tr>
            <td bgcolor="{_GRAY_BG}"
                style="background-color:{_GRAY_BG};padding:20px 40px;
                       border-top:1px solid {_BORDER};text-align:center;">
              <p style="margin:0;font-size:12px;color:{_MUTED};">
                منصة <strong style="color:{_RED};">دمي</strong>
                &nbsp;—&nbsp; شبكة التبرع بالدم في قطاع غزة
              </p>
              <p style="margin:6px 0 0;font-size:11px;color:#94a3b8;">
                هذا البريد أُرسل تلقائياً — يُرجى عدم الرد عليه.
              </p>
            </td>
          </tr>

        </table>
        <!-- /Card -->

      </td>
    </tr>
  </table>
  <!-- /Outer wrapper -->

</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# Outbound email functions
# ─────────────────────────────────────────────────────────────────────────────

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

    name = user.get_full_name() or user.email
    body_html = """\
<p>شكراً لانضمامك إلى <strong>منصة دمي</strong>.</p>
<p>
  لإتمام تسجيلك والبدء في إنقاذ الأرواح، يرجى تأكيد عنوان بريدك
  الإلكتروني بالنقر على الزر أدناه.
</p>"""

    html = _build_email_html(
        greeting=f'مرحباً {name}،',
        body_html=body_html,
        cta_text='تأكيد البريد الإلكتروني',
        cta_url=verify_url,
        footer_note='هذا الرابط صالح لمدة <strong>24 ساعة</strong> فقط. '
                    'إذا لم تقم بالتسجيل يمكنك تجاهل هذه الرسالة.',
    )
    return send_email(
        to=user.email,
        subject='تأكيد بريدك الإلكتروني — منصة دمي',
        html_body=html,
    )


def send_urgent_request_email(donor, blood_request, dashboard_url: str, profile_url: str = '') -> bool:
    """
    Notify a single eligible donor about a new urgent blood request.

    Called by blood_requests/signals.py for each matching donor after a new
    BloodRequest is created. Returns True on success, False on failure.

    profile_url is used in the footer so the donor can disable notifications
    directly from the email.
    """
    name         = donor.get_full_name() or donor.email
    hospital     = blood_request.hospital.get_full_name()
    blood_type   = blood_request.blood_type_needed
    city         = str(blood_request.hospital.city)
    address      = blood_request.hospital_branch_address
    bags         = blood_request.bags_required

    body_html = f"""\
<p>
  تم تسجيل <strong>حالة عاجلة</strong> تطابق فصيلة دمك وتحتاج إلى مساعدتك.
</p>

<!-- Info card -->
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:{_RED_LIGHT};border-radius:10px;
              border:1px solid {_BORDER};margin:20px 0;">
  <tr>
    <td style="padding:20px 24px;direction:rtl;">

      <!-- Blood type badge -->
      <div style="display:inline-block;background:{_RED};color:#fff;
                  font-size:22px;font-weight:800;padding:8px 18px;
                  border-radius:8px;margin-bottom:16px;
                  letter-spacing:1px;">
        {blood_type}
      </div>

      <table cellpadding="0" cellspacing="0" border="0" style="width:100%;">
        <tr>
          <td style="padding:6px 0;font-size:14px;color:{_TEXT};">
            <strong>المستشفى:</strong>&nbsp; {hospital}
          </td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:14px;color:{_TEXT};">
            <strong>المدينة:</strong>&nbsp; {city}
          </td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:14px;color:{_TEXT};">
            <strong>العنوان:</strong>&nbsp; {address}
          </td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:14px;color:{_TEXT};">
            <strong>الأكياس المطلوبة:</strong>&nbsp; {bags}
          </td>
        </tr>
      </table>

    </td>
  </tr>
</table>

<p style="color:{_MUTED};font-size:14px;">
  إذا كنت قادراً على التبرع، انقر على الزر أدناه للذهاب إلى لوحة المتبرع
  وتسجيل التزامك.
</p>"""

    html = _build_email_html(
        greeting=f'مرحباً {name}،',
        body_html=body_html,
        cta_text='عرض الطلب والتسجيل الآن',
        cta_url=dashboard_url,
        footer_note=(
            'تلقيت هذا البريد لأن فصيلة دمك تطابق هذا الطلب العاجل. '
            + (f'يمكنك <a href="{profile_url}" style="color:{_RED};">إيقاف الإشعارات</a> '
               f'من صفحة الملف الشخصي.'
               if profile_url else
               'يمكنك إيقاف الإشعارات من صفحة الملف الشخصي.')
        ),
    )
    return send_email(
        to=donor.email,
        subject=f'حالة عاجلة — فصيلة {blood_type} في {city}',
        html_body=html,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Core dispatcher
# ─────────────────────────────────────────────────────────────────────────────

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
