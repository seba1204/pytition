"""
Organization route names (single textual source of truth).

Members are fully-qualified route names like "organizations:add_user", so they
can be used directly in :func:`django.urls.reverse` and in `{% url %}` without
accessing `.value`.

Notes
-----
- Keep the namespace string in a single place (module-level constant).
- Use a private class constant `_NS` to avoid repetition in member values.
- Enum members must be unique and stable (safe for refactor and autocomplete).
"""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "consents"

_NS = f"{NAMESPACE}:"


class ConsentRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    CONFIRM = _NS + "confirm"
    RESEND = _NS + "resend_confirmation_email"
    SHOW_SYMPA_SUBSCRIBE_BLOC = _NS + "show_sympa_subscribe_bloc"
