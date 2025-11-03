"""Presets route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "presets"

_NS = f"{NAMESPACE}:"


class PresetRoutes(StrEnum):
    """
    Fully-qualified presets route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    NEW = _NS + "new"
    EDIT = _NS + "edit"
    TOGGLE_FAV = _NS + "toggle_fav"
    DELETE = _NS + "delete"
