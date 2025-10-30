"""
All core Django settings with sane, minimal defaults.

Developers are expected to tweak these in code if needed. Anything can still be
overridden via .env / ENV.
"""

from __future__ import annotations

from pathlib import Path

import django.conf.locale
from django.utils.translation import gettext_lazy

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parents[3]  # repo root
SRC_DIR = BASE_DIR / "src"
BUILD_DIR = BASE_DIR / ".build"
BUILD_DIR.mkdir(exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# Security
# ──────────────────────────────────────────────────────────────────────────────

SECRET_KEY = "CHANGE_ME_IN_PROD"
DEBUG = True
ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1", "[::1]"]

# ──────────────────────────────────────────────────────────────────────────────
# Applications
# ──────────────────────────────────────────────────────────────────────────────

INSTALLED_APPS = [
    # Pytition apps
    "apps.accounts",
    "apps.consents",
    "apps.core",
    "apps.files",
    "apps.moderation",
    "apps.notifications",
    "apps.organizations",
    "apps.petition",
    "apps.petitions",
    "apps.presets",
    "apps.signatures",
    "apps.theming",
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd party
    "maintenance_mode",
    "tinymce",
    "colorfield",
    "widget_tweaks",
    "formtools",
    "phonenumber_field",
    "django_extensions",  # for dev purposes
]

# ──────────────────────────────────────────────────────────────────────────────
# Middleware
# ──────────────────────────────────────────────────────────────────────────────

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # 3rd party
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
]

# ──────────────────────────────────────────────────────────────────────────────
# URL / WSGI / ASGI
# ──────────────────────────────────────────────────────────────────────────────

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# ──────────────────────────────────────────────────────────────────────────────
# Templates
# ──────────────────────────────────────────────────────────────────────────────

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Django built-in
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # Custom
                "apps.theming.context_processors.footer_content",
                "apps.core.helpers.settings_context_processor",
                # 3rd party
                "maintenance_mode.context_processors.maintenance_mode",
            ],
        },
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Database
# ──────────────────────────────────────────────────────────────────────────────

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BUILD_DIR / "db.sqlite3"),
    }
}
# FIXME: migrate to BigAutoField later
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# ──────────────────────────────────────────────────────────────────────────────
# Password validation
# ──────────────────────────────────────────────────────────────────────────────

# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 9},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.BCryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# ──────────────────────────────────────────────────────────────────────────────
# Internationalization — auto-discover languages from LOCALE_PATHS
# ──────────────────────────────────────────────────────────────────────────────

TIME_ZONE = "Europe/Paris"
USE_I18N = True  # Activate Django's translation system.
USE_TZ = True  # Use timezone-aware datetimes.
USE_L10N = True  # Format dates, numbers and calendars according to the current locale.

LOCALE_PATHS = [BASE_DIR / "locale"]  # for makemessages

# Supported languages
# In theory, it would be possible to dynamically fetch languages from LOCALE_PATHS
# that are well translated (eg. >95%), but this adds unjustified complexity.
LANGUAGES = [
    ("en", gettext_lazy("English")),
    ("es", gettext_lazy("Spanish")),
    ("fr", gettext_lazy("French")),
    ("it", gettext_lazy("Italian")),
    ("oc", gettext_lazy("Occitan")),
]

LOGOUT_REDIRECT_URL = "/"

EXTRA_LANG_INFO = {
    "oc": {
        "code": "oc",
        "name": "Occitan",
    },
}
LANG_INFO = dict(django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO)
django.conf.locale.LANG_INFO = LANG_INFO

# ──────────────────────────────────────────────────────────────────────────────
# Static & Media
# ──────────────────────────────────────────────────────────────────────────────

STATIC_URL = "/static/"
STATIC_ROOT = str(BUILD_DIR / "static")
STATICFILES_DIRS = [BASE_DIR / "assets"]
ASSETS_DIR = STATICFILES_DIRS[0]

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BUILD_DIR / "media")

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ──────────────────────────────────────────────────────────────────────────────
# Auth / Redirects
# ──────────────────────────────────────────────────────────────────────────────

LOGIN_URL = "/petition/login/"
LOGIN_REDIRECT_URL = "/"

# ──────────────────────────────────────────────────────────────────────────────
# Security headers
# ──────────────────────────────────────────────────────────────────────────────

X_FRAME_OPTIONS = "SAMEORIGIN"
