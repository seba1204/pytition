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


class AccountsConfig(AppConfig):
    name = "apps.accounts"
