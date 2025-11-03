"""
User accounts and profile management.

Handles authentication glue, profile utilities, and user-related signals.
Provides initialization hooks for account-specific behavior.

Notes
-----
- May connect signals in ``AppConfig.ready()``.
- Exposes helpers used by other domain apps.

See Also
--------
organizations, petitions
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class AccountsConfig(AppConfig):
    name = "apps.accounts"

    # Translators: Consent application verbose name (in the admin interface)
    verbose_name = _lazy("Account management")

    def ready(self) -> None:
        # Import signal handlers to connect them
        import apps.accounts.signals  # noqa
