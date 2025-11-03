"""Search URL declarations built from the SearchRoute enum."""

from __future__ import annotations

from apps.core import views as CV
from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.core.routes import SearchRoute

app_name = "core.search"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every SearchRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[SearchRoute, Route] = {
    SearchRoute.SEARCH: Route("", CV.search),
    SearchRoute.PROFILES: Route("profiles", CV.search_profiles),
    SearchRoute.USERS: Route("users", CV.search_users),
}

# Fail fast at import time (CI-friendly)
validate_bijection(SearchRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
