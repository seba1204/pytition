"""
User consent and multi-opt-in flows.

Manages email confirmations and newsletter subscription status to ensure
compliance and explicit consent tracking.

Notes
-----
- Integrates with email delivery and session state.
- Keep domain rules independent from view concerns when possible.

See Also
--------
accounts, signatures
"""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _lazy


class ConsentsConfig(AppConfig):
    name = "apps.consents"
    # Translators: Consent application verbose name (in the admin interface)
    verbose_name = _lazy("Consent management")
