from __future__ import annotations

from typing import TYPE_CHECKING

from django.http import Http404, HttpRequest
from django.utils.translation import gettext as _

from apps.petition.helpers import get_session_user

# Avoid circular imports for type checking
if TYPE_CHECKING:
    from apps.petition.models import Organization, Petition


# Return a 404 if a petition does not exist
def petition_from_id(id: int) -> Petition:
    from apps.petition.models import Petition  # noqa

    petition: Petition | None = Petition.by_id(id)
    if petition is None:
        raise Http404(_("Petition does not exist"))
    else:
        return petition


# Check if a petition is publicly accessible
def check_petition_is_accessible(
    request: HttpRequest, petition: Petition
) -> bool | None:
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
