"""Organization route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "org"

_NS = f"{NAMESPACE}:"


class OrgRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    CREATE = _NS + "create"
    PROFILE = _NS + "profile"
    DASHBOARD = _NS + "dashboard"
    LEAVE = _NS + "leave"
    # TODO: move it to presets routes
    NEW_TEMPLATE = _NS + "new_template"
    # LEGACY
    SLUG_SHOW_PETITION = _NS + "slug_show_petition"
