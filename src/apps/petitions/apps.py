"""
Petition creation, publication, and display.

Core domain app handling petition life cycles, templates, and user interactions.

Notes
-----
- Keep validation and business rules close to models/services.
- Coordinate with signatures for confirmation flows.

See Also
--------
signatures, organizations
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class PetitionsConfig(AppConfig):
    name = "apps.petitions"
    # Translators: Petition application verbose name (in the admin interface)
    verbose_name = _lazy("Petition management")

    def ready(self) -> None:
        # Import signal handlers to connect them
        import apps.petitions.signals  # noqa
