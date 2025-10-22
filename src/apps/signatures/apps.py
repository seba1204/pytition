"""
Petition signatures and confirmation flows.

Handles collection, validation, and confirmation of signatures attached
to petitions.

Notes
-----
- Integrates with consent/email confirmation logic.
- Provide helpers to surface recent actions in the UI.

See Also
--------
petitions, consents
"""

from django.apps import AppConfig


class SignaturesConfig(AppConfig):
    name = "apps.signatures"
