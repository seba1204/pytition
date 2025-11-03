"""Org Invitations route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

from .main import NAMESPACE as ORG_NS

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "invitations"

_NS = f"{ORG_NS}:{NAMESPACE}:"


class OrgInvitationRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    ACCEPT = _NS + "accept"
    DISMISS = _NS + "dismiss"
