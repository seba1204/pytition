"""
Notifications app config.

Handle all mail logic (sending, templating, etc.).
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = "apps.notifications"
    verbose_name = "Notifications"
