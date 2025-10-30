"""View to add a user to an organization."""

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    JsonResponse,
)
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.core.exceptions import ApiError, ConflictError, ForbiddenError, NotFoundError
from apps.organizations.models import Organization

# TODO: move models to apps/{organizations/accounts}/models.py
from apps.petition.models import PytitionUser


# HELPER FUNCTION
def _check_org_context(
    current_user: PytitionUser, orgslugname: str, username: str
) -> tuple[PytitionUser, Organization]:
    """
    Helper function to check organization context and permissions.

    Parameters
    ----------
    current_user : PytitionUser
        The current logged-in user.
    orgslugname : str
        The slugname of the organization.
    username : str
        The username of the user to add.
    Returns
    -------
    tuple[PytitionUser, Organization]
        A tuple containing, the user to add and the organization.
    Raises
    ------
    ApiError
        If any of the checks fail.
    """

    user_to_add = PytitionUser.objects.filter(user__username=username).first()
    if not user_to_add:
        raise NotFoundError(_("This user does not exist (any longer?)"))

    org = Organization.objects.filter(slugname=orgslugname).first()
    if not org:
        raise NotFoundError(_("This organization does not exist (any longer?)"))

    if org not in current_user.organization_set.all():
        raise ForbiddenError(_("You are not part of this organization."))

    if not org.is_allowed_to(current_user, "can_add_members"):
        raise ForbiddenError(
            _("You are not allowed to invite new members into this organization.")
        )

    if org in user_to_add.organization_set.all():
        raise ConflictError(
            _("User is already member of {orgname} organization").format(
                orgname=org.name
            )
        )

    return user_to_add, org


# PATH : org/<slug:orgslugname>/add_user
# Add an user to an organization
@login_required
def add_user(request: HttpRequest, orgslugname: str) -> JsonResponse:
    """
    View function to add a user to an organization.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str
        The slugname of the organization.

    Returns
    -------
    JsonResponse
        A JSON response indicating success or failure of the operation.
    """

    # Get the username of the user to add from GET parameters
    username: str = (request.GET.get("user", "") or "").strip()
    current_user: PytitionUser = get_session_user(request)

    try:
        user_to_add, org = _check_org_context(current_user, orgslugname, username)

        # action
        user_to_add.invitations.add(org)
        user_to_add.save()

        msg: str = _("You invited {username} to join {orgname}").format(
            username=user_to_add.name, orgname=org.name
        )
        return JsonResponse({"message": msg}, status=200)

    except ApiError as e:
        return JsonResponse({"message": e.message}, status=e.status)
    except Exception:
        return JsonResponse({"message": _("An error occurred")}, status=500)
