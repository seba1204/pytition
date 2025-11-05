"""Small delta for test/CI."""

from ..helpers.configure_db import DatabaseSettingsType

DEBUG = False
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


# In-memory sqlite by default for speed

_sqlite_db: DatabaseSettingsType = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

DATABASES = {"default": _sqlite_db}
