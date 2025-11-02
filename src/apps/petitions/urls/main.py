"""
Petitions URL declarations built from the PetitionsRoute enum.

This module maps each :class:`PetitionsRoute` member to an actual Django URL pattern
and view, validates the bijection, and exposes `urlpatterns`.

Note
-----
- cf. :mod:`apps.organizations.urls` for an example of how to use this module.
"""

from __future__ import annotations

from django.urls import include, path
from django.views.generic import RedirectView

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.petitions import forms as PF
from apps.petitions import views as PV
from apps.petitions.routes import SLUG_NS, PetitionsRoute

app_name = "petitions"

PID = "<int:petition_id>"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every PetitionsRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[PetitionsRoute, Route] = {
    # collections
    PetitionsRoute.ALL_PETITIONS: Route(
        "all", RedirectView.as_view(pattern_name="index", permanent=False)
    ),
    PetitionsRoute.NEW: Route(
        "new/", PF.PetitionCreationWizard.as_view(PF.WizardForms)
    ),
    # items
    PetitionsRoute.DELETE: Route(f"{PID}/delete/", PV.delete),
    PetitionsRoute.PUBLISH: Route(f"{PID}/publish/", PV.publish),
    PetitionsRoute.UNPUBLISH: Route(f"{PID}/unpublish/", PV.unpublish),
    PetitionsRoute.EDIT: Route(f"{PID}/edit/", PV.edit),
    PetitionsRoute.TRANSFER: Route(f"{PID}/transfer/", PV.transfer),
    PetitionsRoute.DETAIL: Route(f"{PID}/", PV.detail),
}

# Fail fast at import time (CI-friendly)
validate_bijection(PetitionsRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)

urlpatterns += [
    path(f"{PID}/slug/", include("apps.petitions.urls.slug", namespace=SLUG_NS))
]
