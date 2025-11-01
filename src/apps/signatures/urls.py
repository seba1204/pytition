"""Search URL declarations built from the SignatureRoute enum."""

from __future__ import annotations

from django.urls import URLPattern

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.signatures import views as SV
from apps.signatures.routes import SignatureRoute

app_name = "signatures"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every SignatureRoute must appear exactly once
# --------------------------------------------------------------------------- #


ROUTES: dict[SignatureRoute, Route] = {
    SignatureRoute.NEW: Route("new/", SV.new),
    SignatureRoute.LIST: Route("list/", SV.list_view),
    SignatureRoute.EXPORT: Route("export/", SV.export),
    SignatureRoute.CONFIRM: Route("confirm/<confirmation_hash>", SV.confirm),
    SignatureRoute.RESEND_EMAIL: Route("resend/<int:signature_id>", SV.resend),
}

# Fail fast at import time (CI-friendly)c
validate_bijection(SignatureRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
