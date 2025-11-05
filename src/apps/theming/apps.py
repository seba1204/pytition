"""
Theming app configuration.

Handle all theming logic (styles, templates, etc.).
"""

from django.apps import AppConfig


class ThemingConfig(AppConfig):
    """Configuration for the theming application."""

    name = "apps.theming"
    # Translators: Theming application verbose name (in the admin interface)
    verbose_name = "Theming"
