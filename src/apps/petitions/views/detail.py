"""Detail view for Petition (read-only render mode)."""

from __future__ import annotations

from typing import Any

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from apps.accounts.models import PytitionUser
from apps.accounts.services import get_session_user
from apps.organizations.models import Organization
from apps.petitions.helpers import check_petition_is_accessible
from apps.petitions.models import Petition, SlugModel
from apps.petitions.routes import PetitionsRoute


def detail(request: HttpRequest, petition_id: int) -> HttpResponse:
    """
    Render a petition in view mode.

    Parameters
    ----------
    request : HttpRequest
        Incoming request.
    petition_id : int
        ID of the petition to display.

    Returns
    -------
    HttpResponse
        Rendered page using the unified ``render.html`` template.
    """
    petition: Petition = get_object_or_404(Petition, pk=petition_id)
    # if user is connected, get pytitionuser
    can_edit = False
    if request.user.is_authenticated:
        pytitionuser = get_session_user(request)
        can_edit = petition.is_allowed_to_edit(pytitionuser)
    context: dict[str, Any] = {
        "petition": petition,
        "mode": "view",
        "can_edit": can_edit,
    }
    return render(request, "petitions/render.html", context)


def legacy_detail(
    request: HttpRequest,
    orgslugname: str | None = None,
    username: str | None = None,
    petitionname: str | None = None,
) -> HttpResponse:
    """
    LEGACY: Render a petition by its owner (user/org) and petition slug.

    Parameters
    ----------
    request : HttpRequest
        Incoming request.
    orgslugname : str | None
        Slug name of the organization owning the petition (if any).
    username : str | None
        Username of the user owning the petition (if any).
    petitionname : str
        Slug name of the petition.

    Returns
    -------
    HttpResponse
        Rendered page using the unified ``render.html`` template.
    """
    # permanent redirect to the new URL structure

    if orgslugname:
        try:
            org = Organization.objects.get(slugname=orgslugname)
            slug = SlugModel.objects.get(slug=petitionname, petition__org=org)
        except (Organization.DoesNotExist, SlugModel.DoesNotExist):
            raise Http404(_("Sorry, we are not able to find this petition.")) from None
        petition = slug.petition
    else:
        try:
            user = PytitionUser.objects.get(user__username=username)
            slug = SlugModel.objects.get(slug=petitionname, petition__user=user)
        except PytitionUser.DoesNotExist:
            raise Http404(_("Sorry, we are not able to find this petition.")) from None
        except SlugModel.DoesNotExist:
            raise Http404(_("Sorry, we are not able to find this petition.")) from None
        petition = slug.petition
        check_petition_is_accessible(request, petition)

    return redirect(PetitionsRoute.DETAIL, petition_id=petition.id)
