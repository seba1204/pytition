from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from apps.petition.helpers import check_petition_is_accessible
from apps.petition.models import Signature
from apps.petitions.helpers import petition_from_id


# /<int:petition_id>/confirm/<confirmation_hash>
# Confirm signature to a petition
def confirm(
    request: HttpRequest, petition_id: int, confirmation_hash: str
) -> HttpResponse:
    """
    Confirm a signature to a petition.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    petition_id : int
        The ID of the petition.
    confirmation_hash : str
        The confirmation hash for the signature.
    Returns
    -------
    HttpResponse
        A redirect response to the petition detail page with a success or error message.
    """

    petition = petition_from_id(petition_id)
    check_petition_is_accessible(request, petition)
    try:
        success_msg = petition.confirm_signature(confirmation_hash)
        if success_msg is None:
            messages.error(
                request,
                _(
                    "Error: This confirmation code is invalid. "
                    "Maybe you've already confirmed?"
                ),
            )
        else:
            messages.success(request, success_msg)
            request.session["just_confirmed"] = True
    except ValidationError as e:
        messages.error(request, _(str(e.message)))
    except Signature.DoesNotExist:
        messages.error(request, _("Error: This confirmation code is invalid."))
    return redirect(petition.url)
