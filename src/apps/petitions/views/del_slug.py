from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.accounts.routes import AccountsRoute
from apps.accounts.services import get_session_user
from apps.organizations.models import Organization
from apps.organizations.routes import OrgRoute
from apps.petition.models import Petition, SlugModel
from apps.petitions.helpers import petition_from_id
from apps.petitions.routes import PetitionsRoute


# /<int:petition_id>/del_slug
# Remove a slug from a petition
@login_required
def del_slug(request: HttpRequest, petition_id: int) -> HttpResponse:
    pytitionuser = get_session_user(request)
    petition: Petition
    try:
        petition = petition_from_id(petition_id)
    except Exception:
        messages.error(request, _("This petition does not exist (anymore?)."))
        return redirect(AccountsRoute.DASHBOARD)
    if petition.is_allowed_to_edit(pytitionuser):
        slug_id = request.GET.get("slugid", None)
        if not slug_id:
            return redirect(
                reverse(PetitionsRoute.EDIT, args=[petition_id])
                + "#tab_social_network_form"
            )

        slug = SlugModel.objects.get(pk=slug_id)
        petition.del_slug(slug)
        petition.save()
        messages.success(request, _("Successful deletion of a slug"))
    else:
        messages.error(request, _("You don't have the permission to modify petitions"))
        if petition.owner_type == "org":
            org: Organization = petition.owner  # type: ignore
            return redirect(OrgRoute.DASHBOARD, org.slugname)
        else:
            return redirect(AccountsRoute.DASHBOARD)
    return redirect(
        reverse(PetitionsRoute.EDIT, args=[petition_id]) + "#tab_social_network_form"
    )
