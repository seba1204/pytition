"""Organizations members URL declarations built from the OrgMemberRoute enum."""

from __future__ import annotations

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.organizations.routes import OrgMemberRoute
from apps.organizations.views import members as MV

app_name = "org.members"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every OrgMemberRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[OrgMemberRoute, Route] = {
    OrgMemberRoute.ADD: Route("add", MV.add),
    OrgMemberRoute.DELETE: Route("delete", MV.delete),
    OrgMemberRoute.EDIT_PERMS: Route("<user_name>/perms/edit", MV.edit_perms),
    OrgMemberRoute.SET_PERMS: Route("<user_name>/perms/set", MV.set_perms),
}

# Fail fast at import time (CI-friendly)
validate_bijection(OrgMemberRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns = build_urlpatterns(ROUTES)
