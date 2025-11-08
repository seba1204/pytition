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
    # LEGACY
    LEGACY_DETAIL = _NS + "legacy_detail"
