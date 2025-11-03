"""Small delta for development."""

DEBUG = True

# dev convenience
ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS: list[str] = []

# Email backend for development - prints emails to the console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Default email addresses for development
DEFAULT_FROM_EMAIL = "no-reply@localhost"
SERVER_EMAIL = "server@localhost"
