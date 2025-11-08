"""URL declarations built from the ThemingRoute enum."""

from __future__ import annotations

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.theming import views as TV
from apps.theming.routes import ThemingRoute

app_name = "signatures"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every ThemingRoute must appear exactly once
# --------------------------------------------------------------------------- #


ROUTES: dict[ThemingRoute, Route] = {
    ThemingRoute.CSS: Route("<slug>.css/", TV.css),
}

# Fail fast at import time (CI-friendly)c
validate_bijection(ThemingRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
