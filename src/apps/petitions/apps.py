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


class PetitionsConfig(AppConfig):
    name = "apps.petitions"
