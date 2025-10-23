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


class ConsentsConfig(AppConfig):
    name = "apps.consents"
