"""Petitions route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "petitions"

_NS = f"{NAMESPACE}:"


class PetitionsRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    DETAIL = _NS + "detail"
    DELETE = _NS + "delete"
    PUBLISH = _NS + "publish"
    UNPUBLISH = _NS + "unpublish"
    EDIT = _NS + "edit"
    TRANSFER = _NS + "transfer"
    ALL_PETITIONS = _NS + "all"
    NEW = _NS + "new"
