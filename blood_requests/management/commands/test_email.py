"""
Management command: test_email
Usage:
    python manage.py test_email donor@example.com
Sends a sample urgent-request email to the given address so you can verify
the SMTP backend, template rendering, and spam-folder behaviour in one shot.
"""
from django.core.management.base import BaseCommand, CommandError

from accounts.email_service import send_email, _build_email_html
from accounts.email_service import (
    _NAVY, _TEAL, _TEAL_DARK, _TEAL_LIGHT, _TEAL_SUBTLE,
    _BLOOD_RED, _TEXT, _MUTED, _WHITE,
)


class Command(BaseCommand):
    help = 'Send a test urgent-request email to verify the mail backend.'

    def add_arguments(self, parser):
        parser.add_argument('email', help='Recipient email address')

    def handle(self, *args, **options):
        to = options['email']
        self.stdout.write(f'Sending test email to {to} …')

        body_html = f"""\
<p style="margin:0 0 20px;">
  هذا بريد تجريبي للتحقق من إعدادات الإيميل في منصة
  <strong style="color:{_NAVY};">دمي</strong>.
</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0"
       style="background:{_TEAL_LIGHT};border-radius:12px;
              border:1px solid {_TEAL_SUBTLE};margin:4px 0 20px;">
  <tr>
    <td style="padding:22px 24px;direction:rtl;">
      <div style="display:inline-block;
                  background:linear-gradient(135deg,{_BLOOD_RED} 0%,#B91C1C 100%);
                  color:#fff;font-size:20px;font-weight:800;
                  padding:9px 22px;border-radius:9px;margin-bottom:18px;
                  letter-spacing:1.5px;">
        A+
      </div>
      <table cellpadding="0" cellspacing="0" border="0" style="width:100%;">
        <tr><td style="padding:5px 0;font-size:14px;color:{_TEXT};">
          <span style="color:{_TEAL_DARK};font-weight:700;">المستشفى</span>
          &nbsp;·&nbsp; مستشفى ناصر
        </td></tr>
        <tr><td style="padding:5px 0;font-size:14px;color:{_TEXT};">
          <span style="color:{_TEAL_DARK};font-weight:700;">المدينة</span>
          &nbsp;·&nbsp; خان يونس
        </td></tr>
        <tr><td style="padding:5px 0;font-size:14px;color:{_TEXT};">
          <span style="color:{_TEAL_DARK};font-weight:700;">الأكياس المطلوبة</span>
          &nbsp;·&nbsp; 3
        </td></tr>
      </table>
    </td>
  </tr>
</table>

<p style="color:{_MUTED};font-size:14px;margin:0;">
  هذا بريد اختبار فقط — لا يوجد طلب حقيقي مرتبط به.
</p>"""

        html = _build_email_html(
            greeting='مرحباً،',
            body_html=body_html,
            cta_text='عرض لوحة المتبرع',
            cta_url='http://127.0.0.1:8000/donor/dashboard/',
            footer_note='هذا بريد تجريبي أُرسل من أداة <strong>test_email</strong>.',
        )

        ok = send_email(to=to, subject='[اختبار] إشعار حالة عاجلة — منصة دمي', html_body=html)

        if ok:
            self.stdout.write(self.style.SUCCESS(f'✓ Email dispatched to {to}'))
        else:
            raise CommandError(f'✗ Failed to send email to {to} — check logs above.')
