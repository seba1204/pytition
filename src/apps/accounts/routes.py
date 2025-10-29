"""
Accounts route names (single textual source of truth).

Members are fully-qualified route names like "accounts:dashboard", so they
can be used directly in :func:`django.urls.reverse` and in `{% url %}`.

Notes
-----
- Keep the namespace string in a single place (module-level constant).
- Use a private class constant `_NS` to avoid repetition in member values.
- Enum members must be unique and stable (safe for refactor and autocomplete).
"""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "accounts"

_NS = f"{NAMESPACE}:"


class AccountsRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    DASHBOARD = _NS + "dashboard"  # old user_dashboard
    PUBLIC_PROFILE = _NS + "public_profile"  # old user_profile
    SETTINGS = _NS + "settings"  # old account_settings
    REGISTER = _NS + "register"
