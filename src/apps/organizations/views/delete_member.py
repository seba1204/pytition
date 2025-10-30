"""View to delete a member from an organization."""

from django.contrib.auth.decorators import login_required
from django.http import (
    Http404,
    HttpRequest,
    JsonResponse,
)
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.organizations.models import Organization

# TODO: move models to apps/{organizations/accounts}/models.py
from apps.petition.models import Permission, PytitionUser


# /org/<slug:orgslugname>/delete_member
# Remove a member from an organization
@login_required
def delete_member(request: HttpRequest, orgslugname: str) -> JsonResponse:
    """
    View function to delete a member from an organization.

    Parameters:
    -----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slug name of the organization.
    Returns:
    --------
    JsonResponse
        A JSON response indicating success or failure.
    """

    member_name = request.GET.get("member", "")
    try:
        member = PytitionUser.objects.get(user__username=member_name)
    except PytitionUser.DoesNotExist:
        raise Http404(_("User does not exist")) from None

    pytitionuser = get_session_user(request)

    try:
        org = Organization.objects.get(slugname=orgslugname)
    except Organization.DoesNotExist:
        raise Http404(_("Organization does not exist")) from None

    if pytitionuser not in org.members.all():
        return JsonResponse({}, status=403)  # Forbidden

    try:
        permissions = Permission.objects.get(user=pytitionuser, organization=org)
    except Permission.DoesNotExist:
        return JsonResponse({}, status=500)

    if permissions.can_remove_members or pytitionuser == member:
        if org in member.organization_set.all():
            if org.is_last_admin(member):
                return JsonResponse({}, status=403)  # Forbidden
            member.organization_set.remove(org)
        else:
            return JsonResponse({}, status=404)
    else:
        return JsonResponse({}, status=403)  # Forbidden

    return JsonResponse({}, status=200)
