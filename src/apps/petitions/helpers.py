from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import Http404, HttpRequest
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.petitions.routes import PetitionsRoute

# Avoid circular imports for type checking
if TYPE_CHECKING:
    from apps.organizations.models import Organization
    from apps.petitions.models import Petition


# Return a 404 if a petition does not exist
def petition_from_id(id: int) -> Petition:
    """Get a Petition by its ID or raise 404 if it does not exist."""
    from apps.petitions.models import Petition  # noqa

    petition: Petition | None = Petition.by_id(id)
    if petition is None:
        raise Http404(_("Petition does not exist."))
    else:
        return petition


# Check if a petition is publicly accessible
def check_petition_is_accessible(
    request: HttpRequest, petition: Petition
) -> bool | None:
    """
    Check if the petition is publicly accessible.

    Return True if accessible, None if not accessible, or raise 404 if moderated.
    """
    if petition.published and not petition.moderated:
        return True
    if request.user.is_authenticated:
        user = get_session_user(request)
        if petition.owner_type == "user" and user == petition.owner:
            return True
        if petition.owner_type == "org":
            org: Organization = petition.owner  # type: ignore
            if user in org.members.all():
                return True
    if petition.moderated:
        raise Http404(_("This Petition has been moderated!"))
    if not petition.published:
        raise Http404(_("This Petition is not published yet!"))
    return None


# Generate a meta url for the HTML meta property
def petition_detail_meta(request: HttpRequest, petition_id: int) -> dict[str, str]:
    """Generate the full URL to the petition detail page."""
    detail_path = reverse(PetitionsRoute.DETAIL, args=[petition_id])
    url = f"{request.scheme}://{request.get_host()}{detail_path}"
    return {"site_url": request.get_host(), "petition_url": url}
