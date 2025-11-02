"""Org members route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

from .main import NAMESPACE as ORG_NS

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "members"

_NS = f"{ORG_NS}:{NAMESPACE}:"


class OrgMemberRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    ADD = _NS + "add"
    DELETE = _NS + "delete"
    EDIT_PERMS = _NS + "edit_perms"
    SET_PERMS = _NS + "set_perms"
