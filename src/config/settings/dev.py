from .base import *

DEBUG = True
SECRET_KEY = 'my secret key here'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]', 'pytition3-dev.le.mas']
CSRF_TRUSTED_ORIGINS = ['https://pytition3-dev.le.mas', 'http://pytition3-dev.le.mas']
WHITENOISE_AUTOREFRESH = True
WHITENOISE_USE_FINDERS = True
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
