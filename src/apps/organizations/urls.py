"""
Organizations URL declarations built from the OrgRoute enum.

This module maps each :class:`OrgRoute` member to an actual Django URL pattern
and view, validates the bijection, and exposes `urlpatterns`.

Usage
-----
- Project router:
    path("org/", include("apps.organizations.urls", namespace=NAMESPACE))
- In Python:
    reverse(f"{NAMESPACE}:{OrgRoute.ADD_USER.value}")
    # or with helper: reverse(fq_name(NAMESPACE, OrgRoute.ADD_USER))
- In templates (with the generic context processor below):
    {% url ORG_NS|add:":"|add:ORG_ROUTE.ADD_USER %}
"""

from __future__ import annotations

from django.urls import URLPattern

from apps.core.route import Route, build_urlpatterns, validate_bijection
from apps.organizations import views as OV
from apps.organizations.routes import OrgRoute
from apps.petitions import views as PV
from apps.presets import views as PrV

app_name = "organizations"

SLUG = "<slug:orgslugname>"

# --------------------------------------------------------------------------- #
# One-to-one mapping: every OrgRoute must appear exactly once
# --------------------------------------------------------------------------- #

ROUTES: dict[OrgRoute, Route] = {
    OrgRoute.CREATE: Route("create", OV.create),
    OrgRoute.PROFILE: Route(f"{SLUG}", OV.profile),
    OrgRoute.DASHBOARD: Route(f"{SLUG}/dashboard", OV.dashboard),
    OrgRoute.LEAVE: Route(f"{SLUG}/leave_org", OV.leave),
    OrgRoute.ADD_USER: Route(f"{SLUG}/add_user", OV.add_user),
    # TODO: should be merged with "/presets/new", cf. ticket #52
    OrgRoute.NEW_TEMPLATE: Route(f"{SLUG}/new_template", PrV.new),
    OrgRoute.DELETE_MEMBER: Route(f"{SLUG}/delete_member", OV.delete_member),
    OrgRoute.INVITE_ACCEPT: Route(f"{SLUG}/invite_accept", OV.invite_accept),
    OrgRoute.INVITE_DISMISS: Route(f"{SLUG}/invite_dismiss", OV.invite_dismiss),
    OrgRoute.EDIT_USER_PERMS: Route(
        f"{SLUG}/edit_user_permissions/<user_name>", OV.edit_user_perms
    ),
    OrgRoute.SET_USER_PERMS: Route(
        f"{SLUG}/set_user_permissions/<user_name>", OV.set_user_perms
    ),
    OrgRoute.SLUG_SHOW_PETITION: Route(
        f"{SLUG}/<slug:petitionname>", PV.slug_show_petition
    ),
}

# Fail fast at import time (CI-friendly)
validate_bijection(OrgRoute, ROUTES)

# Short-named patterns; the namespace is supplied by include(..., namespace=NAMESPACE)
urlpatterns: list[URLPattern] = build_urlpatterns(ROUTES)
