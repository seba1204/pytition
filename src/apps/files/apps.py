"""Apps configuration for the Files application."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class FilesConfig(AppConfig):
    """Configuration for the Files application."""

    name = "apps.files"
    # Translators: Files application verbose name (in the admin interface)
    verbose_name = _lazy("Files Management")
