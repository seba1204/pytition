from typing import TypedDict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpRequest,
    HttpResponse,
)
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from apps.organizations.routes import OrgRoute
from apps.petition.helpers import get_session_user, petition_from_id
from apps.petition.models import Organization, Petition, PytitionUser
from apps.petitions.routes import PetitionsRoute


class _TransferContext(TypedDict, total=False):
    user: PytitionUser
    org: Organization
    petition: Petition
    base_template: str


# /transfer_petition/<int:petition_id>
# Transfer a petition to another org or user
@login_required
def transfer(request: HttpRequest, petition_id: int) -> HttpResponse:  # noqa
    """Transfer a petition to another organization or user account."""
    pytitionuser = get_session_user(request)
    petition: Petition
    try:
        petition = petition_from_id(petition_id)
    except Exception:
        messages.error(request, _("This petition does not exist."))
        return redirect("user_dashboard")

    ctx: _TransferContext = {"user": pytitionuser, "petition": petition}
    org: Organization
    # Permission checks
    if petition.owner_type == "org":
        org = petition.owner  # type: ignore
        if not org.is_allowed_to(pytitionuser, "can_modify_permissions"):
            messages.error(
                request,
                _(
                    "You don't have the permission to transfer a petition from "
                    "Organization '{}'".format(org)
                ),
            )
            return redirect(OrgRoute.DASHBOARD, org.slugname)
        ctx["base_template"] = "org/base.html"
        ctx["org"] = org
    elif petition.owner_type == "user":
        if petition.user != pytitionuser:
            messages.error(
                request, _("You don't have the permission to transfer this petition")
            )
            return redirect("user_dashboard")
        ctx["base_template"] = "petition/user_base.html"

    if request.method == "GET":
        return render(request, "petition/transfer_petition.html", ctx)

    if request.method == "POST":
        owner_type = request.POST.get("new_owner_type", "")
        new_owner_name = request.POST.get("new_owner_name", "")
        user = None
        orga: Organization | None = None

        if not owner_type or not new_owner_name:
            messages.error(request, _("Incorrect request, something went wrong."))
            return render(request, "petition/transfer_petition.html", ctx)

        not_found = False
        if owner_type == "org":
            try:
                orga = Organization.objects.get(slugname=new_owner_name)
            except Exception:
                not_found = True
        elif owner_type == "user":
            if settings.DISABLE_USER_PETITION:
                messages.error(
                    request,
                    _(
                        "Users are not allowed to transfer petitions to organizations "
                        "on this instance."
                    ),
                )
                return redirect("user_dashboard")
            try:
                user = PytitionUser.objects.get(user__username=new_owner_name)
            except Exception:
                not_found = True

        if not_found:
            messages.error(
                request, _("You tried to transfer a petition to a non-exiting account")
            )
            return redirect(PetitionsRoute.TRANSFER, petition.id)

        try:
            petition.transfer_to(user, orga)
            # To prevent sending an unwanted published petition to an organization.
            petition.unpublish()
            messages.success(request, _("Petition successfully transfered!"))
            return redirect("user_dashboard")
        except ValueError:
            messages.error(
                request, _("Something went wrong while transferring this petition.")
            )
            return redirect(PetitionsRoute.TRANSFER, petition.id)

    # Default fallback if method is not GET or POST
    return redirect("user_dashboard")
