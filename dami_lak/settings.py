"""
Django settings for dami_lak project.

Environment is controlled entirely through environment variables (or a .env
file in the project root).  No secrets belong in this file.

Quick-start for local development
──────────────────────────────────
Create  dami_lak/.env  (never commit it):

    SECRET_KEY=any-random-string
    DEBUG=True
    ALLOWED_HOSTS=127.0.0.1,localhost

    # Email — pick ONE block:
    # [A] Brevo (also works on PythonAnywhere free)
    BREVO_API_KEY=xkeysib-...
    DEFAULT_FROM_EMAIL=دمي <you@example.com>

    # [B] Gmail SMTP (local / paid hosting only)
    # GMAIL_USER=you@gmail.com
    # GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx

    # [C] Leave everything empty → emails printed to console

Quick-start for PythonAnywhere production
──────────────────────────────────────────
Create  ~/dami_lak/.env  on PythonAnywhere with:

    SECRET_KEY=<generate a strong key>
    DEBUG=False
    ALLOWED_HOSTS=dami2.pythonanywhere.com
    SITE_URL=https://dami2.pythonanywhere.com
    BREVO_API_KEY=xkeysib-...
    DEFAULT_FROM_EMAIL=دمي <your-verified-sender@example.com>

Then run once in a PythonAnywhere Bash console:
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py collectstatic --noinput

And in the Web tab → Static files, add the mapping:
    URL: /static/    Directory: /home/dami2/dami_lak/staticfiles
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# ── Core ──────────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'django-insecure-o&ihbsh&*(^-+dp^svkstxzuma1&xy8182a&gyj9cf5w6=7un%',
)

DEBUG = os.getenv('DEBUG', 'True') == 'True'

_allowed = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]

AUTH_USER_MODEL = 'accounts.User'

# ── Apps ──────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # third-party
    'anymail',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    # project apps
    'accounts',
    'donors.apps.DonorsConfig',
    'hospitals',
    'blood_requests',
    'donations.apps.DonationsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dami_lak.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'donors.context_processors.urgent_requests',
            ],
        },
    },
]

WSGI_APPLICATION = 'dami_lak.wsgi.application'

# ── Database ──────────────────────────────────────────────────────────────────

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ── Auth ──────────────────────────────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL          = '/accounts/login/'
LOGIN_REDIRECT_URL = '/donor/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# ── Internationalisation ───────────────────────────────────────────────────────

LANGUAGE_CODE = 'ar'
TIME_ZONE     = 'Asia/Hebron'
USE_I18N      = True
USE_TZ        = True

# ── Static files ──────────────────────────────────────────────────────────────

STATIC_URL       = '/static/'
STATIC_ROOT      = BASE_DIR / 'staticfiles'   # target of `collectstatic`
STATICFILES_DIRS = [BASE_DIR / 'static']       # your hand-written static files

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Crispy Forms ──────────────────────────────────────────────────────────────

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK          = 'bootstrap5'

# ── Security headers ──────────────────────────────────────────────────────────

SECURE_BROWSER_XSS_FILTER    = True
X_FRAME_OPTIONS              = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF  = True
CSRF_COOKIE_SAMESITE         = 'Strict'
SESSION_COOKIE_HTTPONLY      = True

if not DEBUG:
    # Enforce HTTPS cookies in production
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE    = True

# ── Site URL (used in email links) ────────────────────────────────────────────

SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')

# ── Email ──────────────────────────────────────────────────────────────────────
#
# Priority:  1. Brevo API (HTTPS — works on PythonAnywhere free accounts)
#            2. Gmail SMTP (local dev / paid hosting with SMTP access)
#            3. Console    (fallback — emails printed to terminal)

_brevo_key      = os.getenv('BREVO_API_KEY', '')
_gmail_user     = os.getenv('GMAIL_USER', '')
_gmail_password = os.getenv('GMAIL_APP_PASSWORD', '')
_from_email     = os.getenv('DEFAULT_FROM_EMAIL', '')

if _brevo_key:
    EMAIL_BACKEND      = 'anymail.backends.brevo.EmailBackend'
    ANYMAIL            = {'BREVO_API_KEY': _brevo_key}
    DEFAULT_FROM_EMAIL = _from_email or 'دمي <noreply@dami.ps>'

elif _gmail_user and _gmail_password:
    EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST          = 'smtp.gmail.com'
    EMAIL_PORT          = 587
    EMAIL_USE_TLS       = True
    EMAIL_HOST_USER     = _gmail_user
    EMAIL_HOST_PASSWORD = _gmail_password
    DEFAULT_FROM_EMAIL  = _from_email or f'دمي <{_gmail_user}>'

else:
    EMAIL_BACKEND      = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = _from_email or 'دمي <noreply@dami.ps>'

# ── Logging ───────────────────────────────────────────────────────────────────

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[%(levelname)s] %(name)s: %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'blood_requests': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
        'accounts':       {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dami',     
        'USER': 'root',              
        'PASSWORD': 'root', 
        'HOST': 'localhost',        
        'PORT': '3306',             
    }
}
