"""View to dismiss an invitation to an organization."""

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.organizations.models import Organization


# /org/<slug:orgslugname>/invite_dismiss
# Dismiss the invitation to an organization
@login_required
def dismiss(request: HttpRequest, orgslugname: str) -> HttpResponse:
    """
    View function to dismiss an invitation to an organization.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slugname of the organization.
    Returns
    -------
    HttpResponse
        A redirect to the user dashboard.
    Raises
    ------
    Http404
        If the organization does not exist or there is no invitation.
    """

    if orgslugname == "":
        return JsonResponse({}, status=500)

    pytitionuser = get_session_user(request)

    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        raise Http404(_("not found")) from None

    if org in pytitionuser.invitations.all():
        try:
            pytitionuser.invitations.remove(org)
        except Exception:
            return JsonResponse({}, status=500)
    else:
        raise Http404(_("not found"))

    return redirect(AccountsRoute.DASHBOARD)
