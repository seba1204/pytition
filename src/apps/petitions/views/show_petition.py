"""View to accept an invitation to an organization."""

from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _

# TODO: move forms to apps/signatures/forms.py
from apps.petition.forms import SignatureForm

# TODO: move get_session_user to apps/accounts/services.py
from apps.petition.helpers import (
    check_petition_is_accessible,
    get_session_user,
    petition_detail_meta,
)

# TODO: move models to apps/{organizations/accounts}/models.py
from apps.petition.models import ModerationReason, Organization, PytitionUser, SlugModel
from apps.signatures.helpers import hide_sign_form_if_user_just_signed


# GET /org/<slug:orgslugname>/<slug:petitionname>
# Show a petition
def slug_show_petition(
    request: HttpRequest,
    orgslugname: str | None = None,
    username: str | None = None,
    petitionname: str | None = None,
) -> HttpResponse:
    """
    View function to show a petition.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.
    orgslugname : str | None
        The slugname of the organization.
    username : str | None
        The username of the petition owner.
    petitionname : str | None
        The slugname of the petition.
    Returns
    -------
    HttpResponse
        The HTTP response object with the petition details.
    Raises
    ------
    Http404
        If the petition does not exist or is not accessible.
    """

    try:
        pytitionuser = get_session_user(request)
    except Exception:
        pytitionuser = None

    if orgslugname:
        try:
            org = Organization.objects.get(slugname=orgslugname)
            slug = SlugModel.objects.get(slug=petitionname, petition__org=org)
        except (Organization.DoesNotExist, SlugModel.DoesNotExist):
            raise Http404(_("Sorry, we are not able to find this petition")) from None
        petition = slug.petition
    else:
        try:
            user = PytitionUser.objects.get(user__username=username)
            slug = SlugModel.objects.get(slug=petitionname, petition__user=user)
        except PytitionUser.DoesNotExist:
            raise Http404(_("Sorry, we are not able to find this petition")) from None
        except SlugModel.DoesNotExist:
            raise Http404(_("Sorry, we are not able to find this petition")) from None
        petition = slug.petition
    check_petition_is_accessible(request, petition)
    sign_form = SignatureForm(petition=petition)

    reasons = ModerationReason.objects.all()
    ctx = {
        "user": pytitionuser,
        "petition": petition,
        "form": sign_form,
        "meta": petition_detail_meta(request, petition.id),
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
        return render(request, "petition/petition_detail.html", ctx)
