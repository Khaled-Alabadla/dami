import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

VERIFICATION_TOKEN_MAX_AGE = 60 * 60 * 24  # 24 hours

# ── Brand colours (mirrors :root in static/css/main.css) ─────────────────────
_NAVY        = '#14213D'   # --primary
_NAVY_DARK   = '#10192F'   # --primary-dark
_NAVY_SUBTLE = '#EEF2FF'   # --primary-light
_TEAL        = '#00B8A9'   # --teal
_TEAL_DARK   = '#089184'   # --teal-dark
_TEAL_LIGHT  = '#F0FDFA'   # --teal-light
_TEAL_SUBTLE = '#CCFBF1'   # --teal-subtle
_AMBER       = '#FFC857'   # --accent
_BLOOD_RED   = '#DC2626'   # urgent / blood-type badge only
_GRAY_BG     = '#F4F6F8'   # --bg
_TEXT        = '#0F172A'   # --text
_MUTED       = '#64748B'   # --text-sec
_BORDER      = '#E2E8F0'   # --border
_WHITE       = '#FFFFFF'


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
        f'<p style="margin:28px 0 0;font-size:13px;color:{_MUTED};line-height:1.8;'
        f'background:{_TEAL_LIGHT};border-right:3px solid {_TEAL};'
        f'border-radius:0 6px 6px 0;padding:12px 16px;">{footer_note}</p>'
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
                      border-radius:16px;overflow:hidden;
                      border:1px solid {_BORDER};
                      box-shadow:0 4px 24px rgba(15,23,42,0.10);">

          <!-- ── Top accent bar: Navy → Teal gradient ─────────────────── -->
          <tr>
            <td height="5"
                style="background:linear-gradient(90deg,{_NAVY} 0%,{_TEAL} 100%);
                       font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- ── Header ───────────────────────────────────────────────── -->
          <tr>
            <td bgcolor="{_NAVY}"
                style="background:{_NAVY};padding:26px 40px;">
              <table cellpadding="0" cellspacing="0" border="0" width="100%">
                <tr>
                  <td valign="middle">
                    <span style="font-size:26px;font-weight:800;
                                 color:{_WHITE};letter-spacing:-0.3px;
                                 font-family:Tahoma,Arial,sans-serif;">
                      دمي
                    </span>
                    <span style="font-size:12px;color:rgba(255,255,255,0.50);
                                 padding-right:12px;
                                 border-right:1px solid rgba(255,255,255,0.18);
                                 margin-right:12px;
                                 font-family:Tahoma,Arial,sans-serif;">
                      منصة التبرع بالدم
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- ── Teal accent stripe under header ──────────────────────── -->
          <tr>
            <td height="3"
                style="background:{_TEAL};font-size:0;line-height:0;">&nbsp;</td>
          </tr>

          <!-- ── Body ─────────────────────────────────────────────────── -->
          <tr>
            <td style="padding:36px 40px 32px;direction:rtl;text-align:right;">

              <!-- Greeting -->
              <p style="margin:0 0 20px;font-size:18px;font-weight:700;
                        color:{_TEXT};line-height:1.5;">
                {greeting}
              </p>

              <!-- Body content -->
              <div style="font-size:15px;line-height:1.9;color:#475569;">
                {body_html}
              </div>

              <!-- CTA button -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0"
                     style="margin:32px 0 28px;">
                <tr>
                  <td align="right">
                    <a href="{cta_url}"
                       style="display:inline-block;
                              background:linear-gradient(135deg,{_TEAL} 0%,{_TEAL_DARK} 100%);
                              color:{_WHITE};text-decoration:none;
                              font-size:15px;font-weight:700;
                              padding:14px 40px;border-radius:9px;
                              letter-spacing:0.3px;
                              box-shadow:0 4px 14px rgba(0,184,169,0.35);">
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
                منصة
                <strong style="color:{_NAVY};">دمي</strong>
                &nbsp;—&nbsp; شبكة التبرع بالدم في قطاع غزة
              </p>
              <p style="margin:6px 0 0;font-size:11px;color:#94A3B8;">
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
<p style="margin:0 0 20px;">
  تم تسجيل <strong style="color:{_NAVY};">حالة عاجلة</strong>
  تطابق فصيلة دمك وتحتاج إلى مساعدتك.
</p>

<!-- Info card -->
<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:{_TEAL_LIGHT};border-radius:12px;
              border:1px solid {_TEAL_SUBTLE};margin:4px 0 20px;">
  <tr>
    <td style="padding:22px 24px;direction:rtl;">

      <!-- Blood type badge -->
      <div style="display:inline-block;
                  background:linear-gradient(135deg,{_BLOOD_RED} 0%,#B91C1C 100%);
                  color:#fff;font-size:20px;font-weight:800;
                  padding:9px 22px;border-radius:9px;margin-bottom:18px;
                  letter-spacing:1.5px;
                  box-shadow:0 3px 10px rgba(220,38,38,0.30);">
        {blood_type}
      </div>

      <table cellpadding="0" cellspacing="0" border="0" style="width:100%;">
        <tr>
          <td style="padding:5px 0;font-size:14px;color:{_TEXT};">
            <span style="color:{_TEAL_DARK};font-weight:700;">المستشفى</span>
            &nbsp;·&nbsp; {hospital}
          </td>
        </tr>
        <tr>
          <td style="padding:5px 0;font-size:14px;color:{_TEXT};">
            <span style="color:{_TEAL_DARK};font-weight:700;">المدينة</span>
            &nbsp;·&nbsp; {city}
          </td>
        </tr>
        <tr>
          <td style="padding:5px 0;font-size:14px;color:{_TEXT};">
            <span style="color:{_TEAL_DARK};font-weight:700;">العنوان</span>
            &nbsp;·&nbsp; {address}
          </td>
        </tr>
        <tr>
          <td style="padding:5px 0;font-size:14px;color:{_TEXT};">
            <span style="color:{_TEAL_DARK};font-weight:700;">الأكياس المطلوبة</span>
            &nbsp;·&nbsp; {bags}
          </td>
        </tr>
      </table>

    </td>
  </tr>
</table>

<p style="color:{_MUTED};font-size:14px;margin:0;">
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
            + (f'يمكنك <a href="{profile_url}" style="color:{_TEAL_DARK};">إيقاف الإشعارات</a> '
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

    Returns True on success, False on any exception.
    The full exception is always written to the logger so it appears
    in the PythonAnywhere error log (or the dev console).
    """
    text_body = text_body or _strip_html(html_body)
    logger.debug(
        'Sending email | backend=%s | from=%s | to=%s | subject=%s',
        settings.EMAIL_BACKEND,
        settings.DEFAULT_FROM_EMAIL,
        to,
        subject,
    )
    try:
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to],
            html_message=html_body,
            fail_silently=False,
        )
        logger.debug('Email sent successfully to %s', to)
        return True
    except Exception as exc:
        logger.exception('Failed to send email to %s — %s: %s', to, type(exc).__name__, exc)
        return False


def _strip_html(html: str) -> str:
    """Convert a simple HTML string to plain text for multipart emails."""
    return (
        html
        .replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        .replace('<p>', '').replace('</p>', '\n')
        .replace('<strong>', '').replace('</strong>', '')
    )
