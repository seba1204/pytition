from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from apps.accounts.services import get_session_user
from apps.petition.helpers import sanitize_html
from apps.petitions.helpers import petition_from_id


# <int:petition_id>/show_sympa_subscribe_bloc
# Show sympa subscribe bloc to mass subscribe people to newsletter
@login_required
def show_sympa_subscribe_bloc(request: HttpRequest, petition_id: int) -> HttpResponse:
    """
    Show the sympa subscribe bloc for a petition's newsletter.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    petition_id : int
        The ID of the petition.
    Returns
    -------
    HttpResponse
        An HTTP response containing the sympa subscribe bloc
        or a redirect to the index page.
    """

    try:
        pytitionuser = get_session_user(request)
    except Exception:
        pytitionuser = None

    if not pytitionuser:
        return redirect("index")

    petition = petition_from_id(petition_id)

    if (
        petition.owner_type == "org"
        and petition.org is not None
        and not petition.org.is_allowed_to(pytitionuser, "can_view_signatures")
        or petition.owner_type == "user"
        and petition.owner != pytitionuser
    ):
        return redirect("index")

    text_bloc = ""
    signatures = petition.signature_set.filter(subscribed_to_mailinglist=True)
    if not signatures:
        return HttpResponse(_("No newsletter subscription yet!"))

    for signature in signatures:
        text_bloc = (
            text_bloc
            + f"{signature.email} {signature.first_name} {signature.last_name}<br/>\n"
        )

    return HttpResponse(sanitize_html(text_bloc))
