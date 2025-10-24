"""
Accounts URL declarations built from the AccountsRoute enum.

This module maps each :class:`AccountsRoute` member to an actual Django URL pattern
and view, validates the bijection, and exposes `urlpatterns`.

Note
-----
- cf. :mod:`apps.organizations.urls` for an example of how to use this module.
"""

from __future__ import annotations

from django.urls import URLPattern

from apps.accounts import views as AV  # account views
from apps.accounts.routes import AccountsRoute
from apps.core.routes import Route, build_urlpatterns, validate_bijection

app_name = "accounts"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every AccountsRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[AccountsRoute, Route] = {
    AccountsRoute.DASHBOARD: Route("dashboard", AV.dashboard),
    AccountsRoute.SETTINGS: Route("settings", AV.settings),
    # this one must be last, as it is a catch-all for usernames
    AccountsRoute.PUBLIC_PROFILE: Route("<user_name>", AV.profile),
}

# Fail fast at import time (CI-friendly)
validate_bijection(AccountsRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
