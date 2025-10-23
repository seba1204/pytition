"""Show the dashboard of an organization."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

# TODO: move get_session_user to apps/accounts/services.py
from apps.petition.helpers import get_session_user

# TODO: move models to apps/organizations/models.py
from apps.petition.models import Organization, Permission


# /org/<slug:orgslugname>/dashboard
@login_required
def dashboard(request: HttpRequest, orgslugname: str) -> HttpResponse:
    """
    Show the dashboard of an organization.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slugname of the organization.

    Returns
    -------
    HttpResponse
        The HTTP response object with the rendered dashboard.
    """

    # Check that the organization exists
    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        messages.error(
            request, _("This organization does not exist: '{}'".format(orgslugname))
        )
        return redirect("user_dashboard")

    pytitionuser = get_session_user(request)

    # Check that the user is part of the organization
    if pytitionuser not in org.members.all():
        messages.error(
            request, _("You are not part of this organization: '{}'".format(org.name))
        )
        return redirect("user_dashboard")

    # Get the user's permissions for this organization
    try:
        permissions = Permission.objects.get(organization=org, user=pytitionuser)
    except Permission.DoesNotExist:
        messages.error(
            request,
            _(
                "Internal error, cannot find your permissions attached to this "
                "organization ('{orgname}')".format(orgname=org.name)
            ),
        )
        return redirect("user_dashboard")

    # Get whether the user can create petitions
    can_create_petition = org.is_allowed_to(pytitionuser, "can_create_petitions")

    # Get all petitions for this organization
    petitions = org.petition_set.all()
    other_orgs = pytitionuser.organization_set.filter(~Q(name=org.name)).all()

    # Render the dashboard template
    return render(
        request,
        "org/dashboard.html",
        {
            "org": org,
            "user": pytitionuser,
            "other_orgs": other_orgs,
            "petitions": petitions,
            "user_permissions": permissions,
            "can_create_petition": can_create_petition,
            "displaying_dashboard": True,
        },
    )
