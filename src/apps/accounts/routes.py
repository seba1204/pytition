"""Accounts route names (single textual source of truth)."""

from __future__ import annotations

from enum import StrEnum

# Django namespace used in include(..., namespace=NAMESPACE)
NAMESPACE: str = "accounts"

_NS = f"{NAMESPACE}:"


class AccountsRoute(StrEnum):
    """
    Fully-qualified accounts route names.

    Each member is a string equal to "<namespace>:<short>".
    """

    DASHBOARD = _NS + "dashboard"  # old user_dashboard
    PUBLIC_PROFILE = _NS + "public_profile"  # old user_profile
    SETTINGS = _NS + "settings"  # old account_settings
    REGISTER = _NS + "register"
