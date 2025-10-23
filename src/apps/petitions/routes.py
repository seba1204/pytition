"""
Petitions route names (single textual source of truth).

Members are fully-qualified route names like "organizations:add_user", so they
can be used directly in :func:`django.urls.reverse` and in `{% url %}` without
accessing `.value`.

Notes
-----
- Keep the namespace string in a single place (module-level constant).
- Use a private class constant `_NS` to avoid repetition in member values.
- Enum members must be unique and stable (safe for refactor and autocomplete).
"""

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

    DETAIL = _NS + "detail"  # old detail
    DELETE = _NS + "delete"  # old petition_delete
    PUBLISH = _NS + "publish"  # old petition_publish
    UNPUBLISH = _NS + "unpublish"  # old petition_unpublish
    EDIT = _NS + "edit"  # old edit_petition
    ADD_SLUG = _NS + "add_slug"  # old add_new_slug
    DEL_SLUG = _NS + "del_slug"  # old del_slug
    TRANSFER = _NS + "transfer"  # old transfer_petition
    ALL_PETITIONS = _NS + "all"  # old all_petitions
