"""Consents route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "consents"

_NS = f"{NAMESPACE}:"


class ConsentRoute(StrEnum):
    """
    Fully-qualified consents route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    CONFIRM = _NS + "confirm"
    RESEND = _NS + "resend_confirmation_email"
    EXPORT = _NS + "export"
