"""Signature route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "signatures"

_NS = f"{NAMESPACE}:"


class SignatureRoute(StrEnum):
    """
    Fully-qualified signatures route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    NEW = _NS + "new"
    LIST = _NS + "list"
    EXPORT = _NS + "export"
    CONFIRM = _NS + "confirm"
    RESEND_EMAIL = _NS + "resend_confirmation_email"
