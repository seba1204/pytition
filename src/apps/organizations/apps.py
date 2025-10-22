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


class OrganizationsConfig(AppConfig):
    name = "apps.organizations"
