"""Moderation route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "moderation"

_NS = f"{NAMESPACE}:"


class ModerationRoute(StrEnum):
    """
    Fully-qualified moderation route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    REPORT = _NS + "report_petition"
