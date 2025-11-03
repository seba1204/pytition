"""
Notifications app config.

Handle all mail logic (sending, templating, etc.).
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class NotificationsConfig(AppConfig):
    name = "apps.notifications"
    # Translators: Notifications application verbose name (in the admin interface)
    verbose_name = _lazy("Notifications Management")
