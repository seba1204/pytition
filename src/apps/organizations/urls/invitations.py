"""Organizations members URL declarations built from the OrgInvitationRoute enum."""

from __future__ import annotations

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.organizations.routes import OrgInvitationRoute
from apps.organizations.views import invitations as IV

app_name = "org.invitations"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every OrgInvitationRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[OrgInvitationRoute, Route] = {
    OrgInvitationRoute.ACCEPT: Route("accept/", IV.accept),
    OrgInvitationRoute.DISMISS: Route("dismiss/", IV.dismiss),
}

# Fail fast at import time (CI-friendly)
validate_bijection(OrgInvitationRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
