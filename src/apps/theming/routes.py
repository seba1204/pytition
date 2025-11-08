"""Theming app route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "theming"

_NS = f"{NAMESPACE}:"


class ThemingRoute(StrEnum):
    """
    Fully-qualified theme route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    CSS = _NS + "css"
