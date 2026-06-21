"""
Django settings for dami_lak project.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-o&ihbsh&*(^-+dp^svkstxzuma1&xy8182a&gyj9cf5q6=7un%')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

_allowed = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]

AUTH_USER_MODEL = 'accounts.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Hebron'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/donor/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

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

CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'

SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
CSRF_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_HTTPONLY = True

# ───── Site ─────
SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000')

# ───── Gmail SMTP ─────
# Fill GMAIL_USER and GMAIL_APP_PASSWORD in .env to send real emails.
# Leave both empty to fall back to the console backend (development).
#
# How to get an App Password:
#   1. Enable 2-Step Verification on your Google account.
#   2. Go to Google Account → Security → App Passwords.
#   3. Create a password for "Mail" — use the 16-character code here.
_gmail_user = os.getenv('GMAIL_USER', '')
_gmail_password = os.getenv('GMAIL_APP_PASSWORD', '')

if _gmail_user and _gmail_password:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = _gmail_user
    EMAIL_HOST_PASSWORD = _gmail_password
    DEFAULT_FROM_EMAIL = f'دمي <{_gmail_user}>'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'دمي <noreply@dami.ps>'
