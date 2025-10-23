from __future__ import annotations

from django.urls import URLPattern

from apps.consents import views as CV
from apps.consents.routes import ConsentRoute
from apps.core.routes import Route, build_urlpatterns, validate_bijection

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
    ConsentRoute.SHOW_SYMPA_SUBSCRIBE_BLOC: Route(
        "<int:petition_id>/show_sympa_subscribe_bloc",
        CV.show_sympa_subscribe_bloc,
    ),
}

# Fail fast at import time (CI-friendly)
validate_bijection(ConsentRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
