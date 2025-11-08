"""Organizations URL declarations built from the OrgRoute enum."""

from __future__ import annotations

from django.urls import include, path

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.organizations import views as OV
from apps.organizations.routes import INVITATIONS_NS, MEMBERS_NS, OrgRoute
from apps.petitions import views as PV

app_name = "organizations"

SLUG = "<slug:orgslugname>"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every OrgRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[OrgRoute, Route] = {
    OrgRoute.CREATE: Route("create", OV.create),
    OrgRoute.PROFILE: Route(f"{SLUG}", OV.profile),
    OrgRoute.DASHBOARD: Route(f"{SLUG}/dashboard", OV.dashboard),
    OrgRoute.LEAVE: Route(f"{SLUG}/leave", OV.leave),
    # LEGACY
    OrgRoute.LEGACY_DETAIL: Route(f"{SLUG}/<slug:petitionname>", PV.legacy_detail),
}


# Fail fast at import time (CI-friendly)
validate_bijection(OrgRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)

# TODO: [#83] improve build_urlpatterns to handle included namespaces
urlpatterns += [
    path(
        f"{SLUG}/members/",
        include("apps.organizations.urls.members", namespace=MEMBERS_NS),
    ),
    path(
        f"{SLUG}/invitations/",
        include("apps.organizations.urls.invitations", namespace=INVITATIONS_NS),
    ),
]
