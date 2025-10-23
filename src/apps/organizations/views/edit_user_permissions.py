"""View to edit user permissions in an organization."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.organizations.routes import OrgRoute

# TODO: move get_session_user to apps/accounts/services.py
from apps.petition.helpers import get_session_user

# TODO: move models to apps/{organizations/accounts}/models.py
from apps.petition.models import Organization, Permission, PytitionUser


# PATH : org/<slug:orgslugname>/edit_user_permissions/<slug:user_name>
# Show a webpage to edit permissions
@login_required
def edit_user_perms(
    request: HttpRequest, orgslugname: str, user_name: str
) -> HttpResponse:
    """
    View function to show and edit user permissions in an organization.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slugname of the organization.
    user_name : str
        The username of the member whose permissions are to be edited.

    Returns
    -------
    HttpResponse
        A webpage to edit user permissions.

    Raises
    ------
    Http404
        If the organization or user does not exist.
    """

    pytitionuser = get_session_user(request)

    try:
        member = PytitionUser.objects.get(user__username=user_name)
    except PytitionUser.DoesNotExist:
        messages.error(
            request, _("User '{name}' does not exist".format(name=user_name))
        )
        return redirect(OrgRoute.DASHBOARD, orgslugname)

    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        raise Http404(
            _("Organization '{name}' does not exist".format(name=orgslugname))
        ) from None

    if org not in member.organization_set.all():
        messages.error(
            request,
            _(
                "The user '{username}' is not member of "
                "this organization ({orgname}).".format(
                    username=user_name, orgname=org.name
                )
            ),
        )
        return redirect(OrgRoute.DASHBOARD, org.slugname)

    try:
        permissions = Permission.objects.get(organization=org, user=member)
    except Permission.DoesNotExist:
        messages.error(
            request,
            _(
                "Internal error, this member does not have permissions attached "
                "to this organization."
            ),
        )
        return redirect(OrgRoute.DASHBOARD, org.slugname)

    try:
        user_permissions = Permission.objects.get(organization=org, user=pytitionuser)
    except Exception:
        return HttpResponse(
            _(
                "Internal error, cannot find your permissions attached to this "
                "organization ('{orgname}')".format(orgname=org.name)
            ),
            status=500,
        )

    return render(
        request,
        "org/edit_user_perms.html",
        {
            "org": org,
            "member": member,
            "user": pytitionuser,
            "permissions": permissions,
            "user_permissions": user_permissions,
        },
    )
