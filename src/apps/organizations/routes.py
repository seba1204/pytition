"""
Organization route names (single textual source of truth).

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
NAMESPACE: str = "org"

_NS = f"{NAMESPACE}:"


class OrgRoute(StrEnum):
    """
    Fully-qualified organization route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    CREATE = _NS + "create"
    PROFILE = _NS + "profile"
    DASHBOARD = _NS + "dashboard"
    LEAVE = _NS + "leave"
    ADD_USER = _NS + "add_user"
    NEW_TEMPLATE = _NS + "new_template"
    DELETE_MEMBER = _NS + "delete_member"
    INVITE_ACCEPT = _NS + "invite_accept"
    INVITE_DISMISS = _NS + "invite_dismiss"
    EDIT_USER_PERMS = _NS + "edit_user_perms"
    SET_USER_PERMS = _NS + "set_user_perms"
    SLUG_SHOW_PETITION = _NS + "slug_show_petition"
