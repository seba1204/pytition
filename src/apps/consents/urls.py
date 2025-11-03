from __future__ import annotations

from apps.consents import views as CV
from apps.consents.routes import ConsentRoute
from apps.core.route import Route, build_urlpatterns, validate_bijection

app_name = "consents"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every ConsentRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[ConsentRoute, Route] = {
    ConsentRoute.EXPORT: Route(
        "export",
        CV.export,
    ),
}

# Fail fast at import time (CI-friendly)
validate_bijection(ConsentRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
