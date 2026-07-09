"""
Django settings for the Taxon AI site.

This replaces the earlier React + Firebase stack. Classic Django: server-
rendered templates, Django's built-in auth, Django admin for managing users.
"""

import os
from pathlib import Path
import dj_database_url

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Reuses the same .env file at the project root that already existed for the
# old Firebase config. Django only reads the DJANGO_* keys below — it ignores
# the old VITE_FIREBASE_* ones, which are now unused and safe to delete later.
load_dotenv(BASE_DIR / ".env")

# --- Core ---------------------------------------------------------------

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-insecure-key-change-before-deploying",  # fine for local dev only
)

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = ['.vercel.app', '.attonate.com', "localhost", "127.0.0.1"]

# Needed for POST requests (login/signup/contact forms/etc.) to pass Django's
# CSRF check in production — without this, every form submit on the deployed
# site 403s even though GET requests work fine. Add the real custom domain(s)
# here too once DNS is pointed at Vercel.
CSRF_TRUSTED_ORIGINS = [
    "https://*.vercel.app",
    "https://attonate.com",
    "https://www.attonate.com",
]

# Vercel terminates TLS at its edge and forwards to the app over plain HTTP,
# so Django can't tell the request was HTTPS unless it's told to trust this
# header. Without it, request.is_secure() is always False behind Vercel,
# which breaks secure cookies and CSRF's origin/scheme check.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# --- Apps -----------------------------------------------------------------

INSTALLED_APPS = [
    "cloudinary_storage",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "cloudinary",
    "django.contrib.sites",  # required by allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "core",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    # NOTE: the old blanket RequireCompleteProfileMiddleware (accounts/middleware.py)
    # was replaced by a softer approach: a hard redirect right after signup only
    # (see accounts.views.signup_view / core.views.home), a persistent but
    # non-blocking banner site-wide (see accounts.context_processors.profile_status
    # + templates/base.html), and a hard gate specifically on the /apply/ flow
    # (see core.views.apply_view). Browsing the rest of the site stays open.
]

SITE_ID = 1

ROOT_URLCONF = "taxonsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.site_content",
                "accounts.context_processors.profile_status",
            ],
        },
    },
]

WSGI_APPLICATION = "taxonsite.wsgi.application"

# --- Database ---------------------------------------------------------------
# Neon Postgres in production, via DATABASE_URL (set as a Vercel env var —
# never committed). Falls back to local SQLite when DATABASE_URL isn't set,
# so `manage.py runserver` still works without a Neon connection string.

if os.environ.get("DATABASE_URL"):
    DATABASES = {
        "default": dj_database_url.config(
            env="DATABASE_URL",
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Auth -------------------------------------------------------------------

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "core:home"
LOGOUT_REDIRECT_URL = "core:home"

AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrPhoneBackend",  # our own login — email OR phone, both primary keys
    "django.contrib.auth.backends.ModelBackend",  # fallback (e.g. Django admin login)
    "allauth.account.auth_backends.AuthenticationBackend",  # Google login
]

# We only use allauth for the *social* (Google) login — our own SignupForm/
# login views (accounts app) still handle plain email+password. These
# settings tell allauth our User model has no username field, and to skip
# email-confirmation screens/extra signup steps since there's no email
# sending set up yet.
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True  # skip allauth's "confirm connect" click-through page

# Google-verified emails are trustworthy enough that if someone signs in with
# Google using the same email as an existing password account, we log them
# straight into that account instead of blocking with a "sign in first, then
# connect Google" page.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_OAUTH_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", ""),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
    }
}

# --- Internationalization -----------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_TZ = True

# --- Static & media files -------------------------------------------------

STATIC_URL = '/static/'
# Written as BASE_DIR / 'staticfiles' (pathlib style) rather than
# os.path.join(...) to match Vercel's own documented STATIC_ROOT pattern —
# their automatic static-asset detection may parse settings.py for this
# exact form rather than executing it.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# The project's static/ folder lives at the repo root, not inside an app
# (accounts/static/ or core/static/) — Django's static file finders only
# auto-discover per-app static/ dirs, so without this, collectstatic (and
# local runserver) can't see any of these files at all. This was the actual
# cause of every static asset 404ing in production.
STATICFILES_DIRS = [BASE_DIR / "static"]

# Cloudinary Media Storage Configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

# Django 5.1+ unified storage setting.
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# django-cloudinary-storage ships its own collectstatic command (since
# "cloudinary_storage" is in INSTALLED_APPS) that overrides Django's built-in
# one, and that command reads settings.STATICFILES_STORAGE directly — the
# legacy attribute, which Django no longer populates once STORAGES is set
# explicitly. Without this, collectstatic crashes with AttributeError:
# 'Settings' object has no attribute 'STATICFILES_STORAGE'. Keeping both the
# modern STORAGES dict and this legacy scalar (pointed at the same backend)
# satisfies both Django's own code and this third-party package's command.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


# MEDIA_URL = "media/"
# MEDIA_ROOT = BASE_DIR / "media"  # profile photos + resumes land here

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
