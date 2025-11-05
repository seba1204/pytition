"""
Organization profiles, membership, and permissions.

Provides dashboards and utilities for managing organizations and their
members, including role-based access.

Notes
-----
- Views depend on user resolution from the accounts app.

See Also
--------
accounts, petitions
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class OrganizationsConfig(AppConfig):
    """Configuration for the Organizations application."""
    name = "apps.organizations"
    # Translators: Organizations application verbose name (in the admin interface)
    verbose_name = _lazy("Organization management")
