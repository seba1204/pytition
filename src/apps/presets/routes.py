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

    NEW = _NS + "new"  # old user_new_template
    EDIT = _NS + "edit"  # old edit_template
    TOGGLE_FAV = _NS + "toggle_fav"  # old template_fav_toggle
    DELETE = _NS + "delete"  # old template_delete
