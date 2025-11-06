"""View to show petition details."""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from apps.accounts.services import get_session_user
from apps.moderation.models import ModerationReason
from apps.petitions.helpers import (
    check_petition_is_accessible,
    petition_detail_meta,
    petition_from_id,
)
from apps.signatures.forms import SignatureForm
from apps.signatures.helpers import hide_sign_form_if_user_just_signed


# Show information on a petition
def detail(request: HttpRequest, petition_id: int) -> HttpResponse:
    """
    Detail view of a petition.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    petition_id : int
        The ID of the petition to display.

    Returns
    -------
    HttpResponse
        The HTTP response with the petition detail page or JSON data.
    """
    petition = petition_from_id(petition_id)
    check_petition_is_accessible(request, petition)
    try:
        pytitionuser = get_session_user(request)
    except Exception:
        pytitionuser = None

    reasons = ModerationReason.objects.all()
    sign_form = SignatureForm(petition=petition)
    ctx = {
        "user": pytitionuser,
        "petition": petition,
        "form": sign_form,
        "meta": petition_detail_meta(request, petition_id),
        "moderation_reasons": reasons,
        "og_image_absolute_url": request.build_absolute_uri(petition.twitter_image),
    }

    # If we've just signed successfully the petition, do not show the sign form
    hide_sign_form_if_user_just_signed(request, ctx)

    if "application/json" in request.META.get("HTTP_ACCEPT", []):
        response = JsonResponse(petition.to_json)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        return response
    else:
        return render(request, "petitions/detail_bs5.html", ctx)
