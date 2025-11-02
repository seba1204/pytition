"""Petitions slugs URL declarations built from the PetitionsSlugRoute enum."""

from __future__ import annotations

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.petitions.routes import PetitionsSlugRoute
from apps.petitions.views import slug as SV

app_name = "petitions.slug"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every OrgInvitationRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[PetitionsSlugRoute, Route] = {
    PetitionsSlugRoute.ADD: Route("accept/", SV.add),
    PetitionsSlugRoute.DELETE: Route("dismiss/", SV.delete),
}

# Fail fast at import time (CI-friendly)
validate_bijection(PetitionsSlugRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
