from __future__ import annotations

from django.urls import URLPattern

from apps.consents import views as CV
from apps.consents.routes import ConsentRoute
from apps.core.route import Route, build_urlpatterns, validate_bijection

app_name = "consents"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every ConsentRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[ConsentRoute, Route] = {
    ConsentRoute.CONFIRM: Route(
        "<int:petition_id>/confirm/<confirmation_hash>",
        CV.confirm,
    ),
    ConsentRoute.RESEND: Route(
        "resend/<int:signature_id>",
        CV.resend,
    ),
    ConsentRoute.EXPORT: Route(
        "<int:petition_id>/export",
        CV.export,
    ),
}

# Fail fast at import time (CI-friendly)
validate_bijection(ConsentRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
