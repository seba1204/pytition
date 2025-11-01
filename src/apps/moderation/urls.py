"""Search URL declarations built from the ModerationRoute enum."""

from __future__ import annotations

from django.urls import URLPattern

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.moderation import views as MV
from apps.moderation.routes import ModerationRoute

app_name = "moderation"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every ModerationRoute must appear exactly once
# --------------------------------------------------------------------------- #

PET = "report/petition/<int:petition_id>"

ROUTES: dict[ModerationRoute, Route] = {
    # TODO: reason_id should be in optional URL parameter
    ModerationRoute.REPORT: Route(f"{PET}/<int:reason_id>", MV.report),
    ModerationRoute.REPORT: Route(f"{PET}/", MV.report),
}

# Fail fast at import time (CI-friendly)
validate_bijection(ModerationRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
