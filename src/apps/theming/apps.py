"""
Theming app configuration.

Handle all theming logic (styles, templates, etc.).
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class ThemingConfig(AppConfig):
    """Configuration for the theming application."""

    name = "apps.theming"
    # Translators: Theming application verbose name (in the admin interface)
    verbose_name = _lazy("Theming")

    def ready(self) -> None:
        """Import signal handlers."""
        # avoid circular imports
        import apps.theming.signals  # noqa
