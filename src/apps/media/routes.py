"""Media route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "media"

_NS = f"{NAMESPACE}:"


class MediaRoute(StrEnum):
    """
    Fully-qualified media route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    UPLOAD = _NS + "upload"  # old image_upload
