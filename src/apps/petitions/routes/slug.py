"""Petition slugs route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

from .main import NAMESPACE as PETITIONS_NS

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "slug"

_NS = f"{PETITIONS_NS}:{NAMESPACE}:"


class PetitionsSlugRoute(StrEnum):
    """
    Fully-qualified petitions route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    ADD = _NS + "add"
    DELETE = _NS + "delete"
