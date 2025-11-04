"""Apps configuration for the Moderation application."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class ModerationConfig(AppConfig):
    """Configuration for the Moderation application."""

    name = "apps.moderation"
    # Translators: Moderation application verbose name (in the admin interface)
    verbose_name = _lazy("Moderation Management")

    def ready(self) -> None:
        """Perform application initialization tasks."""
        return
