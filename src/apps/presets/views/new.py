"""
View to create a new petition preset.

Handle both organization and user preset creation.
"""

from typing import TypedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.organizations.routes import OrgRoute

# TODO: move get_session_user to apps/accounts/services.py
from apps.petition.helpers import get_session_user

# TODO: move models to apps/{organizations/accounts/petitions}/models.py
from apps.petition.models import (
    Organization,
    Permission,
    PetitionTemplate,
    PytitionUser,
)


class _NewPresetContext(TypedDict, total=False):
    user: PytitionUser
    org: Organization
    user_permissions: Permission
    base_template: str


# /org/<slug:orgslugname>/new_template
# /user/new_template
# Create a new template
@login_required
def new(request: HttpRequest, orgslugname: str | None = None) -> HttpResponse:
    """
    View function to create a new petition preset.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str | None, optional
        The slugname of the organization (if it's an organization preset),
        By default None.
    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered new template page or a redirect.
    """

    pytitionuser: PytitionUser = get_session_user(request)
    ctx: _NewPresetContext = {"user": pytitionuser}

    if orgslugname:
        redirection: str = OrgRoute.NEW_TEMPLATE
        try:
            org = Organization.objects.get(slugname=orgslugname)
            ctx["org"] = org
        except Organization.DoesNotExist:
            raise Http404(_("Organization does not exist")) from None

        if org not in pytitionuser.organization_set.all():
            return HttpResponseForbidden(
                _("You are not allowed to view this organization dashboard")
            )

        try:
            permissions = Permission.objects.get(organization=org, user=pytitionuser)
            ctx["user_permissions"] = permissions
        except Permission.DoesNotExist:
            return HttpResponse(
                _(
                    "Internal error, cannot find your permissions attached to this "
                    "organization ('{orgname}')".format(orgname=org.name)
                ),
                status=500,
            )

        if not permissions.can_create_templates:
            return HttpResponseForbidden(
                _(
                    "You don't have the permission to create a Template in "
                    "this organization"
                )
            )

        ctx["base_template"] = "org/base.html"
    else:
        redirection = "user_new_template"
        ctx["base_template"] = "petition/user_base.html"

    if request.method == "POST":
        template_name = request.POST.get("template_name", "")
        if template_name != "":
            if orgslugname:
                template = PetitionTemplate(name=template_name, org=org)
            else:
                template = PetitionTemplate(name=template_name, user=pytitionuser)
            template.save()
            return redirect("edit_template", template.id)
        else:
            messages.error(request, _("You need to provide a template name."))
            return redirect(redirection)
    else:
        return render(request, "petition/new_template.html", ctx)
