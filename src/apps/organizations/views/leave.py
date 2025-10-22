from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _

# TODO: move get_session_user to apps/accounts/services.py
from apps.petition.helpers import get_session_user

# TODO: move model to apps/organizations/models.py
from apps.petition.models import Organization


# /org/<slug:orgslugname>/leave_org
# User is leaving the organization
@login_required
def leave_org(request: HttpRequest, orgslugname: str) -> HttpResponse:
    """
    View function for a user to leave an organization.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slugname of the organization to leave.

    Returns
    -------
    HttpResponse
        A redirect response to the account settings page.
    """

    # Check that the organization exists
    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        raise Http404(_("not found")) from None

    # Check that the user is part of the organization
    pytitionuser = get_session_user(request)

    if pytitionuser not in org.members.all():
        raise Http404(_("not found"))
    with transaction.atomic():
        if org.is_last_admin(pytitionuser):
            messages.error(
                request,
                _(
                    "Impossible to leave this organization, "
                    "you are the last administrator"
                ),
            )
            return redirect(reverse("account_settings") + "#a_org_form")
        elif org.members.count() == 1:
            messages.error(
                request,
                _("Impossible to leave this organization, you are the last member"),
            )
            return redirect(reverse("account_settings") + "#a_org_form")
        else:
            org.members.remove(pytitionuser)
    return redirect("account_settings")
