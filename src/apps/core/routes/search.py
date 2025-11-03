"""Core search route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "core.search"

_NS = f"{NAMESPACE}:"


class SearchRoute(StrEnum):
    """
    Fully-qualified core search route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    SEARCH = _NS + "search"  # old search
    PROFILES = _NS + "profiles"  # old search_users_and_orgs
    USERS = _NS + "users"  # old get_user_list
